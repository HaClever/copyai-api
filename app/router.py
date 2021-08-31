from fastapi import APIRouter
from selenium_bots import CopyAiSelenium
from enums import TwoFieldOptions, OneFieldOptions

copyai = CopyAiSelenium()

router = APIRouter()


@router.get('/login')
async def login_to_copyai():
    """ Логин в Copy.ai"""
    copyai.log_in_if_not_loggined()


@router.post('/one_field_tools')
async def use_one_field_tool(product_description: str,
                             option: OneFieldOptions = OneFieldOptions.instagram_captions) -> list:
    """ Для работы с инструментами, у которых одно поле """
    copyai.log_in_if_not_loggined()
    copyai.copyai_select_option(option.value)
    return copyai.copyai_get_response(product_description)


@router.post('/two_field_tools')
async def use_two_field_tool(product_description: str, product_name: str,
                             option: TwoFieldOptions = TwoFieldOptions.product_descriptions) -> list:
    """ Для работы с инструментами, у которых два поля """
    copyai.log_in_if_not_loggined()
    copyai.copyai_select_option(option.value)
    return copyai.copyai_get_response(product_description, product_name)
