# TASK: The weekly subscription cost of an app is $7. We expect that 3% of users will choose this subscription option.
# The average life-time of a paid user is 10 weeks.
# The coefficient of free (organic) installations is 10% of the total number of installations.
# The average cost per one install (CPI) is $1.1. Refund rate is 5%.
# How many installations are needed to receive $10,000 in net profit (taking into account a 30% App Store commission
# and paid traffic costs)? How much money do we need to spend to achieve this goal?

# ------- manual calculation ----------
# number of installs - x
# Three calculation parts:
# 1. LTV - 0.03x * 7 * 10
# 2. acquisition cost for paid users - 0.9x * 1.1
# 3. total revenue (with refunds and store comission) - 10000 * 1.05 * 1.3
# Equation:
# 1 part - 2 part = 3 part
# 0.03x * 7 * 10 - 0.9x * 1.1 = 10000 * 1.05 * 1.3
# 2.1x - 0.99x = 13650
# x = 13650 / (2.1 - 0.99)
# x = 12297
# amount of money to spend: 12297 * 0.9 * 1.1 = 12174

# ------ possible additional parameters -----
# We could add other types of subscription calculations. Example:
# 5% of users choose $5 weekly subscription. We add this to LTV (1 part):
# 0.03x * 7 * 10 + 0.05x * 5 * 10
# We could also add general additional spends to 3 part and acquisition costs to 2 part.


def calculate_installs_and_spend(
    sub_cost: int,
    conv_rate: int,
    free_inst_coef: int,
    avg_lifetime: int,
    cpi: float,
    refund_rate: int,
    store_comission: int,
    net_profit: int,
) -> dict[str, int]:
    """
    Calculate number of installations needed and amount to spend for achieving net_profit goal.

    :param sub_cost: subscription cost
    :param conv_rate: percentage of people who subscribe
    :param free_inst_coef: coefficient of free (organic) installations
    :param avg_lifetime: average life-time of a paid user
    :param cpi: cost per installation
    :param refund_rate: refund rate
    :param store_comission: comission of app store
    :param net_profit: goal net profit
    :return: dictionary with number of installations needed and amount to spend values
    """
    conv_rate = round(conv_rate / 100, 2)
    conv_coef = conv_rate * sub_cost * avg_lifetime
    paid_inst_coef = 1 - round(free_inst_coef / 100, 2)
    cpi_coef = paid_inst_coef * cpi
    refund_rate = round(refund_rate / 100, 2)
    store_comission = round(store_comission / 100, 2)
    net_profit_plus_refund = net_profit + net_profit * refund_rate
    net_profit_plus_refund_plus_store_comission = (
        net_profit_plus_refund + net_profit_plus_refund * store_comission
    )
    num_installs = round(
        net_profit_plus_refund_plus_store_comission / (conv_coef - cpi_coef)
    )
    amount_to_spend = round(num_installs * paid_inst_coef * cpi)

    return {"installations_needed": num_installs, "money_to_spend": amount_to_spend}


if __name__ == "__main__":
    print(
        calculate_installs_and_spend(
            sub_cost=7,
            conv_rate=3,
            free_inst_coef=10,
            avg_lifetime=10,
            cpi=1.1,
            refund_rate=5,
            store_comission=30,
            net_profit=10000,
        )
    )
