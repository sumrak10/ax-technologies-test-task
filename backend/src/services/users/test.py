import datetime
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from src.services.users import APIKeyService, JWTService
from src.schemas.users import UserDTO, UserAPIKeyDTO
from src.utils import exceptions


@pytest.mark.asyncio
async def test_api_key_service_create():
    mock_current_user = Mock(spec=UserDTO)
    mock_current_user.id = 1

    mock_session = AsyncMock()

    with patch('src.utils.session_context_manager.SessionContextManager', return_value=mock_session):
        key = await APIKeyService.create(mock_session, mock_current_user,
                                         datetime.date.today() + datetime.timedelta(days=1))
        assert isinstance(key, str)
    with pytest.raises(exceptions.NotAcceptableHTTPException):
        with patch('src.utils.session_context_manager.SessionContextManager', return_value=mock_session):
            key = await APIKeyService.create(mock_session, mock_current_user,
                                             datetime.date.today() - datetime.timedelta(days=1))


@pytest.mark.asyncio
async def test_api_key_service_get_all():
    mock_current_user = Mock(spec=UserDTO)
    mock_current_user.id = 1

    mock_model = Mock()
    mock_model.to_DTO.return_value = UserAPIKeyDTO(id=1, key="key1", user_id=1, expire_date=datetime.date.today(),
                                                   created_at=datetime.datetime.utcnow())

    mock_result = Mock()
    mock_result.all.return_value = [(mock_model,)]

    mock_session = AsyncMock()
    mock_session.session.execute.return_value = mock_result

    with patch('src.utils.session_context_manager.SessionContextManager', mock_session):
        keys = await APIKeyService.get_all(mock_session, mock_current_user)
        assert isinstance(keys, list)
        assert isinstance(keys[0], UserAPIKeyDTO)
        assert len(keys) == 1

