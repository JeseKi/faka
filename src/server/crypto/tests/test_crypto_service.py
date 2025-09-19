# -*- coding: utf-8 -*-
"""
加密服务测试
"""

import pytest
from src.server.crypto.service import encrypt, decrypt


def test_encrypt_decrypt_consistency():
    """测试加解密一致性"""
    original_data = "test_data_123"
    encrypted_data = encrypt(original_data)
    decrypted_data = decrypt(encrypted_data)
    assert original_data == decrypted_data


def test_encrypt_different_output():
    """测试相同输入加密后输出不同"""
    original_data = "test_data_123"
    encrypted_data1 = encrypt(original_data)
    encrypted_data2 = encrypt(original_data)
    assert encrypted_data1 != encrypted_data2


def test_decrypt_invalid_data():
    """测试解密无效数据"""
    with pytest.raises(ValueError):
        decrypt("invalid_encrypted_data")