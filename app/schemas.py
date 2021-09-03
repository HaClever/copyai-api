from pydantic import BaseModel
from enums import TwoFieldOptions, OneFieldOptions

class OneFieldOption(BaseModel):
    option: OneFieldOptions = OneFieldOptions.instagram_captions
    field_value: str = 'Описание продукта'

class TwoFieldOption(BaseModel):
    option: TwoFieldOptions = TwoFieldOptions.product_descriptions
    main_field_value: str = 'Описание продукта'
    secondary_field_value: str = 'Обычно название продукта'
