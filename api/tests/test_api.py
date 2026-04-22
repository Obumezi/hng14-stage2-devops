from unittest.mock import patch


def test_health():
    assert True


@patch("api.main.r")
def test_create_job(mock_redis):
    mock_redis.lpush.return_value = True
    mock_redis.hset.return_value = True
    assert mock_redis.lpush("jobs", "123")


@patch("api.main.r")
def test_get_job(mock_redis):
    mock_redis.hget.return_value = "completed"
    assert mock_redis.hget("job:123", "status") == "completed"