from typing import List
from crud.base import CRUDBase
from models.groups import Groups
from sqlalchemy.orm import Session
from schemas.groups import GroupCreate
from models.groupoptions import GroupOptions

class CRUDGroup(CRUDBase[Groups, GroupCreate, None]):

    # Create Group with options
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

    # Get All Groups
    def get_all(self, db: Session, store_id: str):
        groups = db.query(Groups).filter(Groups.store_id == store_id).all()
        for group in groups:
            group.options = db.query(GroupOptions).filter(GroupOptions.group_id == group.id).all()
        return groups

    # Get Group by ID
    def get_by_id(self, db: Session, store_id: str, group_id: str):
        group = db.query(Groups).filter(Groups.store_id == store_id, Groups.id == group_id).first()

        if not group:
            return None
        
        group.options = db.query(GroupOptions).filter(GroupOptions.group_id == group_id).all()

        return group
    
    # Delete Group by ID
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

    # Get Groups for a Product
    def get_groups_for_product(
        self,
        db: Session,
        shopify_app: str,
        store_id: str,
        product_id: str
    ) -> List[dict]:
        # Step 1: get unique group_ids from GroupOptions
        group_options = db.query(GroupOptions.group_id).filter(
            GroupOptions.shopify_name == shopify_app,
            GroupOptions.store_id == store_id,
            GroupOptions.product_id == product_id
        ).distinct().all()

        group_ids = [g.group_id for g in group_options]

        if not group_ids:
            return []

        # Step 2: get Groups
        groups = db.query(Groups).filter(
            Groups.shopify_name == shopify_app,
            Groups.store_id == store_id,
            Groups.id.in_(group_ids)
        ).all()

        # Step 3: manually attach options for each group
        result = []
        for group in groups:
            options = db.query(GroupOptions).filter(
                GroupOptions.group_id == group.id,
                GroupOptions.shopify_name == shopify_app,
                GroupOptions.store_id == store_id,
                GroupOptions.product_id == product_id
            ).all()

            group_dict = {
                "id": group.id,
                "group_name": group.group_name,
                "type": group.type,
                "store_id": group.store_id,
                "shopify_name": group.shopify_name,
                "options": [
                    {
                        "id": opt.id,
                        "product_id": opt.product_id,
                        "color_code": opt.color_code,
                        "image_url": opt.image_url,
                        "position": opt.position
                    } for opt in options
                ]
            }
            result.append(group_dict)

        return result
        
group = CRUDGroup(Groups)
