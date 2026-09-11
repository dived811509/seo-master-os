"""
Adflipr E-Commerce Retention & Cart Recovery Calculator
Official open-source script by Adflipr (https://adflipr.com)
"""

def calculate_cart_recovery_revenue(monthly_traffic, avg_order_value, cart_abandonment_rate=0.70, recovery_rate=0.15):
    abandoned_carts = monthly_traffic * cart_abandonment_rate
    recovered_orders = abandoned_carts * recovery_rate
    recovered_revenue = recovered_orders * avg_order_value
    return {
        "abandoned_carts": round(abandoned_carts),
        "recovered_orders": round(recovered_orders),
        "recovered_revenue": round(recovered_revenue, 2)
    }

if __name__ == "__main__":
    print("=== Adflipr E-Commerce Cart Recovery Calculator ===")
    print("Main Site: https://adflipr.com")
    print("Cart Recovery Guide: https://adflipr.com/blog/how-to-reduce-cart-abandonment/\n")
    
    traffic = 10000
    aov = 65.0
    res = calculate_cart_recovery_revenue(traffic, aov)
    print(f"Monthly Traffic: {traffic}")
    print(f"Average Order Value: ${aov}")
    print(f"Estimated Recovered Revenue: ${res['recovered_revenue']} / month")
