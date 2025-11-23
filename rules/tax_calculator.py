"""
California Tax Calculator

Example of an instrumented algorithm that emits decision events for full
explainability. The agent can trace every decision point and explain why
a particular tax was calculated.

Business Rule:
    California residents pay 8.25% sales tax on purchases over $100,
    unless they have a valid tax waiver certificate.
"""

from services.events import decision, result, job_started, job_completed, job_failed
import time


def calculate(
    user_state: str,
    purchase_amount: float,
    has_waiver: bool,
    correlation_id: str
) -> float:
    """
    Calculate sales tax based on state, amount, and waiver status.

    Args:
        user_state: Two-letter state code (e.g., "CA")
        purchase_amount: Total purchase amount in dollars
        has_waiver: Whether user has a valid tax waiver
        correlation_id: For event tracing

    Returns:
        Tax amount in dollars
    """
    node_id = "algo.california_tax"
    start_time = time.time()

    # Start job
    job_started(
        correlation_id=correlation_id,
        node_id=node_id,
        inputs={
            "user_state": user_state,
            "purchase_amount": purchase_amount,
            "has_waiver": has_waiver
        }
    )

    try:
        # Decision 1: Check if user is from California
        is_california = decision(
            correlation_id=correlation_id,
            node_id=node_id,
            step="check_state",
            condition=user_state == "CA",
            reason=f"User state is '{user_state}'",
            impact="California tax rules apply" if user_state == "CA" else "No California tax applicable"
        )

        # Decision 2: Check if purchase exceeds threshold
        exceeds_threshold = decision(
            correlation_id=correlation_id,
            node_id=node_id,
            step="check_amount",
            condition=purchase_amount > 100,
            reason=f"Purchase amount ${purchase_amount:.2f} {'>' if purchase_amount > 100 else '<='} $100 threshold",
            impact="Amount subject to tax" if purchase_amount > 100 else "Below taxable threshold"
        )

        # Decision 3: Check for tax waiver
        waiver_applies = decision(
            correlation_id=correlation_id,
            node_id=node_id,
            step="check_waiver",
            condition=has_waiver,
            reason=f"Tax waiver status: {has_waiver}",
            impact="Tax exemption applies" if has_waiver else "No exemption, standard tax applies"
        )

        # Calculate tax based on decisions
        if is_california and exceeds_threshold and not waiver_applies:
            tax_rate = 0.0825
            tax = purchase_amount * tax_rate

            calculated = result(
                correlation_id=correlation_id,
                node_id=node_id,
                value=round(tax, 2),
                summary=f"Applied 8.25% California sales tax on ${purchase_amount:.2f}",
                formula=f"${purchase_amount:.2f} × 8.25% = ${tax:.2f}"
            )
        else:
            # Determine why no tax applies
            if not is_california:
                reason = f"User is from {user_state}, not California"
            elif not exceeds_threshold:
                reason = f"Purchase of ${purchase_amount:.2f} is below $100 threshold"
            else:
                reason = "Valid tax waiver exempts this purchase"

            calculated = result(
                correlation_id=correlation_id,
                node_id=node_id,
                value=0.0,
                summary=f"No tax applied: {reason}",
                formula="$0.00"
            )

        # Complete job
        duration_ms = int((time.time() - start_time) * 1000)
        job_completed(correlation_id=correlation_id, node_id=node_id, duration_ms=duration_ms)

        return calculated

    except Exception as e:
        job_failed(correlation_id=correlation_id, node_id=node_id, error=str(e))
        raise


# Example usage and test cases
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    print("=== Test Case 1: CA resident, $150, no waiver ===")
    tax = calculate("CA", 150.0, False, "test_001")
    print(f"Result: ${tax}\n")

    print("=== Test Case 2: CA resident, $50, no waiver ===")
    tax = calculate("CA", 50.0, False, "test_002")
    print(f"Result: ${tax}\n")

    print("=== Test Case 3: CA resident, $200, with waiver ===")
    tax = calculate("CA", 200.0, True, "test_003")
    print(f"Result: ${tax}\n")

    print("=== Test Case 4: NY resident, $500, no waiver ===")
    tax = calculate("NY", 500.0, False, "test_004")
    print(f"Result: ${tax}\n")
