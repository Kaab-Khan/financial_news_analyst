import os
import pytest
from src.pipeline.price_pipeline import price_pipeline
from dotenv import load_dotenv
load_dotenv()

def test_price_pipeline_real_success():
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        pytest.skip("No API key set for Alpha Vantage")
    result = price_pipeline('AAPL', '2024-01-01', '2024-01-10', api_key)
    assert result['first_day'] is not None
    assert result['first_price'] is not None
    assert result['last_day'] is not None
    assert result['last_price'] is not None
    assert isinstance(result['percentage_change'], float)

def test_price_pipeline_real_invalid_symbol():
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        pytest.skip("No API key set for Alpha Vantage")
    result = price_pipeline('INVALID', '2024-09-01', '2024-09-30', api_key)
    assert result['first_day'] is None
    assert result['first_price'] is None
    assert result['last_day'] is None
    assert result['last_price'] is None
    assert result['percentage_change'] == 0.0

def test_price_pipeline_internal_api_key_success():
    """
    Test price_pipeline without explicitly passing API key and URL.
    It should fetch the API key and URL from environment variables.
    """
    # # Ensure the environment variables are set
    # api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    # api_url = os.getenv('ALPHA_VINTAGE_API_URL')
    # if not api_key or not api_url:
    #     pytest.skip("No API key or URL set in environment variables")

    # Call the pipeline without explicitly passing the API key
    result = price_pipeline('AAPL', '2025-09-01', '2024-09-28')
    for i in result:
        print(i, result[i])
    # Check that we got a valid result structure
    # Assertions
    assert result['first_day'] is not None
    assert result['first_price'] is not None
    assert result['last_day'] is not None
    assert result['last_price'] is not None
    assert 'percentage_change' in result, "Key 'percentage_change' should be in the result"
    assert isinstance(result['percentage_change'], float), "percentage_change should be a float"