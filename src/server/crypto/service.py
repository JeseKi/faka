# -*- coding: utf-8 -*-
"""
加密服务模块

公开接口：
- encrypt(data: str) -> str: 加密数据
- decrypt(encrypted_data: str) -> str: 解密数据

内部方法：
- _generate_key() -> bytes: 生成加密密钥
- _pad(data: bytes) -> bytes: 填充数据
- _unpad(data: bytes) -> bytes: 去除填充

说明：
- 使用 AES 加密算法对数据进行加密和解密
- 生成的密钥基于 UUID 并进行 SHA-256 哈希处理
"""

import base64
import hashlib
import uuid
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class CryptoService:
    def __init__(self):
        """初始化加密服务"""
        self.key = self._generate_key()

    def _generate_key(self) -> bytes:
        """
        生成加密密钥
        
        Returns:
            bytes: 32字节的加密密钥
        """
        # 使用 UUID 生成一个随机字符串，然后进行 SHA-256 哈希处理得到 32 字节的密钥
        unique_string = str(uuid.uuid4())
        return hashlib.sha256(unique_string.encode('utf-8')).digest()

    def _pad(self, data: bytes) -> bytes:
        """
        填充数据以满足 AES 加密的块大小要求
        
        Args:
            data (bytes): 原始数据
            
        Returns:
            bytes: 填充后的数据
        """
        return pad(data, AES.block_size)

    def _unpad(self, data: bytes) -> bytes:
        """
        去除填充数据
        
        Args:
            data (bytes): 填充后的数据
            
        Returns:
            bytes: 原始数据
        """
        return unpad(data, AES.block_size)

    def encrypt(self, data: str) -> str:
        """
        加密数据
        
        Args:
            data (str): 要加密的原始数据
            
        Returns:
            str: Base64 编码的加密数据
        """
        # 生成随机 IV
        iv = uuid.uuid4().bytes[:16]
        
        # 创建 AES 加密器
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        # 加密数据
        padded_data = self._pad(data.encode('utf-8'))
        encrypted_data = cipher.encrypt(padded_data)
        
        # 将 IV 和加密数据组合后进行 Base64 编码
        result = base64.b64encode(iv + encrypted_data).decode('utf-8')
        return result

    def decrypt(self, encrypted_data: str) -> str:
        """
        解密数据
        
        Args:
            encrypted_data (str): Base64 编码的加密数据
            
        Returns:
            str: 解密后的原始数据
            
        Raises:
            ValueError: 当解密失败时抛出异常
        """
        try:
            # Base64 解码
            raw_data = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # 提取 IV 和加密数据
            iv = raw_data[:16]
            encrypted_bytes = raw_data[16:]
            
            # 创建 AES 解密器
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            
            # 解密数据
            decrypted_data = cipher.decrypt(encrypted_bytes)
            
            # 去除填充并转换为字符串
            original_data = self._unpad(decrypted_data).decode('utf-8')
            return original_data
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")


# 创建全局加密服务实例
crypto_service = CryptoService()


def encrypt(data: str) -> str:
    """
    加密数据
    
    Args:
        data (str): 要加密的原始数据
        
    Returns:
        str: Base64 编码的加密数据
    """
    return crypto_service.encrypt(data)


def decrypt(encrypted_data: str) -> str:
    """
    解密数据
    
    Args:
        encrypted_data (str): Base64 编码的加密数据
        
    Returns:
        str: 解密后的原始数据
    """
    return crypto_service.decrypt(encrypted_data)