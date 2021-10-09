from pydantic import BaseModel
from enums import TwoFieldOptions, OneFieldOptions, Tone


class OneFieldOption(BaseModel):
    option: OneFieldOptions = OneFieldOptions.instagram_captions
    field_value: str = "Описание продукта"
    tone: Tone = "Friendly"


class TwoFieldOption(BaseModel):
    option: TwoFieldOptions = TwoFieldOptions.product_descriptions
    main_field_value: str = "Описание продукта"
    secondary_field_value: str = "Обычно название продукта"
    tone: Tone = "Friendly"
