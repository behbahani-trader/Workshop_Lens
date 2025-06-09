from app import create_app, db
from app.models.order import Order

def update_cancelled_orders():
    app = create_app()
    with app.app_context():
        # Get all cancelled orders
        cancelled_orders = Order.query.filter_by(status='cancelled').all()
        print(f"Found {len(cancelled_orders)} cancelled orders")
        
        # Update them to pending
        for order in cancelled_orders:
            order.status = 'pending'
            print(f"Updating order {order.id} from cancelled to pending")
        
        # Commit the changes
        db.session.commit()
        print("All cancelled orders have been updated to pending")

if __name__ == '__main__':
    update_cancelled_orders() 