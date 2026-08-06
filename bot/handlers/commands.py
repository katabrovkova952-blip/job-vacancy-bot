import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.sender import send_digest_to
from vacancies.models import Subscriber
from vacancies.services import parse_keywords

logger = logging.getLogger(__name__)

router = Router()


HELP_TEXT = (
    'Я надсилаю нові вакансії з DOU.\n\n'
    '/start — підписатися або відновити підписку\n'
    '/pause — поставити підписку на паузу\n'
    '/filters — вказати фільтри\n'
    '/help — це повідомлення'
)


@router.message(Command('help'))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    subscriber, created = await Subscriber.objects.aget_or_create(
        chat_id=message.chat.id,
    )

    if created:
        logger.info('Новий підписник: %s', subscriber.chat_id)
        await message.answer(
            'Привіт! Я надсилатиму нові вакансії.\n\n'
            'Спершу вкажи, що тебе цікавить:\n'
            '/filters\n\n'
            'Усі команди — /help'
        )
        return

    if not subscriber.is_active:
        subscriber.is_active = True
        await subscriber.asave(update_fields=['is_active'])
        logger.info('Підписник %s відновив підписку', subscriber.chat_id)
        await message.answer('З поверненням! Підписку відновлено.')
        return

    await message.answer('Ти вже підписаний.')


@router.message(Command('pause'))
async def cmd_pause(message: Message) -> None:
    subscriber = await Subscriber.objects.filter(chat_id=message.chat.id).afirst()
    if subscriber is None:
        await message.answer("Ти ще не підписаний. Натисни /start")
        return

    if not subscriber.is_active:
        await message.answer("Підписка вже на паузі")
        return

    subscriber.is_active = False
    await subscriber.asave(update_fields=['is_active'])
    logger.info('Підписник %s поставив підписку на паузу', subscriber.chat_id)
    await message.answer('Підписку зупинено. Щоб відновити — /start')


class FilterStates(StatesGroup):
    waiting_for_keywords = State()


async def save_filters(message: Message, subscriber: Subscriber, raw: str) -> None:
    keywords = parse_keywords(raw)

    if not keywords:
        await message.answer('Не вдалося розпізнати ключові слова. Спробуй: python, django')
        return

    subscriber.filters = ', '.join(keywords)
    await subscriber.asave(update_fields=['filters'])

    await message.answer(f'Фільтри оновлено: {subscriber.filters}')

    sent = await send_digest_to(message.bot, subscriber)
    if not sent:
        await message.answer('Поки що нових вакансій за цими фільтрами немає.')



@router.message(Command('filters'))
async def cmd_filters(message: Message, command: CommandObject, state: FSMContext) -> None:
    subscriber = await Subscriber.objects.filter(chat_id=message.chat.id).afirst()
    if subscriber is None:
        await message.answer('Спершу натисни /start')
        return

    if command.args:

        await save_filters(message, subscriber, command.args)
        return

    current = subscriber.filters or 'не встановлені'
    await message.answer(f'Поточні фільтри: {current}\n\nНапиши нові ключові слова через кому:')
    await state.set_state(FilterStates.waiting_for_keywords)


@router.message(FilterStates.waiting_for_keywords)
async def process_keywords(message: Message, state: FSMContext) -> None:
    subscriber = await Subscriber.objects.filter(chat_id=message.chat.id).afirst()
    if subscriber is None:
        await state.clear()
        return

    await save_filters(message, subscriber, message.text or '')
    await state.clear()