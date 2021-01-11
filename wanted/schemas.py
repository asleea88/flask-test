import settings
from typing import List
from pydantic import BaseModel, PositiveInt, constr, validator, ValidationError


class CompanyNameArgs(BaseModel):
    value: constr(
        min_length=1,
        max_length=settings.COMPANY_NAME_MAX_LEN
    )


class TagIdsArgs(BaseModel):
    value: str

    @validator('value')
    def act_type_match(cls, v):
        try:
            tag_ids_ = v.split(',')
            if not tag_ids_:
                raise ValidationError

            tag_ids = []

            for tag in tag_ids_:
                tag_ = int(tag)
                if tag_ < 1:
                    raise ValidationError
                tag_ids.append(int(tag_))

        except Exception:
            raise ValidationError

        return tag_ids


class TagInfo(BaseModel):
    id: PositiveInt


class AddCompanyTagReq(BaseModel):
    tags: List[TagInfo]
