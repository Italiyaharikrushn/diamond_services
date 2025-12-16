from sqlalchemy.orm import Session
from crud.base import CRUDBase
from models.groups import Groups
from models.groupoptions import GroupOptions
from schemas.groups import GroupCreate

class CRUDGroup(CRUDBase[Groups, GroupCreate, None]):

    def create(self, db: Session, payload: GroupCreate):
        group = Groups(
            store_id=payload.store_id,
            shopify_name=payload.shopify_name,
            group_name=payload.group_name,
            type=payload.type
        )
        db.add(group)
        db.commit()
        db.refresh(group)

        for option in payload.options:
            group_option = GroupOptions(
                store_id=option.store_id,
                shopify_name=option.shopify_name,
                group_id=group.id,
                product_id=option.product_id,
                color_code=option.color_code,
                image_url=option.image_url,
                position=option.position
            )
            db.add(group_option)

        db.commit()
        return group

    def get_all(self, db: Session):
        groups = db.query(Groups).all()
        for group in groups:
            group.options = db.query(GroupOptions).filter(GroupOptions.group_id == group.id).all()
        return groups

group = CRUDGroup(Groups)
