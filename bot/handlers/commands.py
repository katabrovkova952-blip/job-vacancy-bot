import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.sender import send_digest_to
from bot.texts import DEFAULT_LANGUAGE, TEXTS, t
from vacancies.models import Subscriber
from vacancies.services import parse_keywords

logger = logging.getLogger(__name__)

router = Router()


def detect_language(message: Message) -> str:
    code = (message.from_user.language_code or DEFAULT_LANGUAGE)[:2] if message.from_user else DEFAULT_LANGUAGE
    return code if code in TEXTS else DEFAULT_LANGUAGE


async def get_subscriber(message: Message) -> Subscriber | None:
    return await Subscriber.objects.filter(chat_id=message.chat.id).afirst()


class FilterStates(StatesGroup):
    waiting_for_keywords = State()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    subscriber, created = await Subscriber.objects.aget_or_create(
        chat_id=message.chat.id,
        defaults={'language': detect_language(message)},
    )

    if created:
        logger.info('Новий підписник: %s', subscriber.chat_id)
        await message.answer(t('welcome', subscriber.language))
        return

    if not subscriber.is_active:
        subscriber.is_active = True
        await subscriber.asave(update_fields=['is_active'])
        logger.info('Підписник %s відновив підписку', subscriber.chat_id)
        await message.answer(t('welcome_back', subscriber.language))
        return

    await message.answer(t('already_subscribed', subscriber.language))


@router.message(Command('help'))
async def cmd_help(message: Message) -> None:
    subscriber = await get_subscriber(message)
    language = subscriber.language if subscriber else detect_language(message)
    await message.answer(t('help', language))


@router.message(Command('pause'))
async def cmd_pause(message: Message) -> None:
    subscriber = await get_subscriber(message)

    if subscriber is None:
        await message.answer(t('not_subscribed', detect_language(message)))
        return

    if not subscriber.is_active:
        await message.answer(t('already_paused', subscriber.language))
        return

    subscriber.is_active = False
    await subscriber.asave(update_fields=['is_active'])
    logger.info('Підписник %s поставив підписку на паузу', subscriber.chat_id)
    await message.answer(t('paused', subscriber.language))


@router.message(Command('ua'))
async def cmd_language_uk(message: Message) -> None:
    await set_language(message, 'uk')


@router.message(Command('en'))
async def cmd_language_en(message: Message) -> None:
    await set_language(message, 'en')


async def set_language(message: Message, language: str) -> None:
    subscriber = await get_subscriber(message)

    if subscriber is None:
        await message.answer(t('not_subscribed', detect_language(message)))
        return

    if subscriber.language == language:
        await message.answer(t('language_already', language))
        return

    subscriber.language = language
    await subscriber.asave(update_fields=['language'])
    logger.info('Підписник %s змінив мову на %s', subscriber.chat_id, language)
    await message.answer(t('language_changed', language))


async def save_filters(message: Message, subscriber: Subscriber, raw: str) -> None:
    keywords = parse_keywords(raw)

    if not keywords:
        await message.answer(t('filters_invalid', subscriber.language))
        return

    subscriber.filters = ', '.join(keywords)
    await subscriber.asave(update_fields=['filters'])
    await message.answer(t('filters_updated', subscriber.language, filters=subscriber.filters))

    sent = await send_digest_to(message.bot, subscriber)
    if not sent:
        await message.answer(t('no_vacancies', subscriber.language))


@router.message(Command('filters'))
async def cmd_filters(message: Message, command: CommandObject, state: FSMContext) -> None:
    subscriber = await get_subscriber(message)

    if subscriber is None:
        await message.answer(t('not_subscribed', detect_language(message)))
        return

    if command.args:
        await save_filters(message, subscriber, command.args)
        return

    current = subscriber.filters or t('filters_not_set', subscriber.language)
    await message.answer(
        t('filters_current', subscriber.language, filters=current)
        + '\n\n'
        + t('filters_ask', subscriber.language)
    )
    await state.set_state(FilterStates.waiting_for_keywords)


@router.message(FilterStates.waiting_for_keywords)
async def process_keywords(message: Message, state: FSMContext) -> None:
    subscriber = await get_subscriber(message)

    if subscriber is None:
        await state.clear()
        return

    await save_filters(message, subscriber, message.text or '')
    await state.clear()