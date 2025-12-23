from crud.base import CRUDBase
from models.groups import Groups
from sqlalchemy.orm import Session
from schemas.groups import GroupCreate
from models.groupoptions import GroupOptions

class CRUDGroup(CRUDBase[Groups, GroupCreate, None]):

    def create(self, db: Session, payload: GroupCreate, store_id: str):
        group = Groups(
            store_id=store_id,
            shopify_name=payload.shopify_name,
            group_name=payload.group_name,
            type=payload.type
        )
        db.add(group)
        db.commit()
        db.refresh(group)

        for option in payload.options:
            group_option = GroupOptions(
                store_id=store_id,
                shopify_name=payload.shopify_name,
                group_id=group.id,
                product_id=option.product_id,
                color_code=option.color_code,
                image_url=option.image_url,
                position=option.position
            )
            db.add(group_option)

        db.commit()
        return group

    def get_all(self, db: Session, store_id: str):
        groups = db.query(Groups).filter(Groups.store_id == store_id).all()
        for group in groups:
            group.options = db.query(GroupOptions).filter(GroupOptions.group_id == group.id).all()
        return groups

    def get_by_id(self, db: Session, store_id: str, group_id: str):
        group = db.query(Groups).filter(Groups.store_id == store_id, Groups.id == group_id).first()

        if not group:
            return None
        
        group.options = db.query(GroupOptions).filter(GroupOptions.group_id == group_id).all()

        return group
    
    def delete_by_id(self, db: Session, store_id: str, group_id: str):
        try:
            # delete_group = (db.query(Groups).filter(Groups.store_id == store_id, Groups.id == group_id).update({"status": 0}, synchronize_session=False))
            # deleted_options = (db.query(GroupOptions).filter(GroupOptions.group_id == group_id).update({"status": 0}, synchronize_session=False))
            delete_group = db.query(Groups).filter(Groups.store_id == store_id, Groups.id == group_id).delete(synchronize_session=False)
            deleted_options = db.query(GroupOptions).filter(GroupOptions.group_id == group_id).delete(synchronize_session=False)

            db.commit()
            if delete_group == 0:
                return None
            
            return {"group_id": group_id, "deleted_group": delete_group, "deleted_options": deleted_options}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        
group = CRUDGroup(Groups)
