from app import guards


def test_card_keeps_only_last_4_and_id_is_fully_masked():
    out = guards.mask_pii("My card number is 5412 7512 3412 3456 and my national ID is 29801011234567.")
    assert out == "My card number is [CARD_NUMBER ending 3456] and my national ID is [NATIONAL_ID]."
    assert "5412" not in out and "2980" not in out


def test_card_without_spaces():
    assert guards.mask_pii("card 4111111111111111 please") == "card [CARD_NUMBER ending 1111] please"
