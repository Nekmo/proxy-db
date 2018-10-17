
try:
    from mock import patch, Mock, mock_open, call
except ImportError:
    from unittest.mock import patch, Mock, mock_open, call
