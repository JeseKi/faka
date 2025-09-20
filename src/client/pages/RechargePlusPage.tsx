import React, { useState } from 'react';
import { Button, Card, Form, Input, Space, Steps, Typography } from 'antd';
import { useNavigate } from 'react-router-dom';
import { checkActivationCode, createOrder } from '../lib/order';
import { App } from 'antd';

const { Title, Text } = Typography;
const { TextArea } = Input;

const RechargePlusPage: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [activationCode, setActivationCode] = useState('');
  const [cookies, setCookies] = useState('');
  const [isConfirmChecked, setIsConfirmChecked] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCheckingCode, setIsCheckingCode] = useState(false);
  const navigate = useNavigate();
  const { message } = App.useApp()

  // 步骤1：检验卡密
  const handleCheckCode = async () => {
    if (!activationCode.trim()) {
      message.error('请输入卡密');
      return;
    }

    setIsCheckingCode(true);
    try {
      const result = await checkActivationCode(activationCode);
      if (result.available) {
        setCurrentStep(1);
        message.success('卡密有效');
      } else {
        message.error('卡密无效或已失效');
      }
    } catch (error) {
      console.error('检验卡密失败:', error);
      message.error('检验卡密时发生错误，请稍后再试');
    } finally {
      setIsCheckingCode(false);
    }
  };

  // 步骤2：输入Cookies
  const handleNextToConfirm = () => {
    if (!cookies.trim()) {
      message.error('请输入您的 ChatGPT Cookies');
      return;
    }
    setCurrentStep(2);
  };

  // 步骤3：确认信息并提交订单
  const handleSubmitOrder = async () => {
    if (!isConfirmChecked) {
      message.error('请确认您的信息无误');
      return;
    }

    setIsSubmitting(true);
    try {
      // 调用创建订单的 API
      const orderData = {
        code: activationCode,
        remarks: cookies // 将 cookies 作为备注信息提交
      };
      
      const result = await createOrder(orderData);
      
      // 如果订单创建成功
      console.log('订单创建成功:', result);
      setCurrentStep(3); // 跳转到成功页面
    } catch (error: unknown) {
      console.error('创建订单失败:', error);
      // 根据后端返回的错误信息进行提示
      // 定义一个类型来处理可能的响应错误
      interface ResponseError extends Error {
        response?: {
          data?: {
            detail?: string;
          };
        };
      }
      
      const responseError = error as ResponseError;
      
      if (error instanceof Error && responseError.response?.data?.detail) {
        message.error(`创建订单失败: ${responseError.response.data.detail}`);
      } else {
        message.error('创建订单时发生未知错误，请稍后再试');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // 返回上一步
  const handlePrev = () => {
    setCurrentStep(currentStep - 1);
  };

  // 返回首页
  const handleGoHome = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <Card className="shadow-lg rounded-xl">
          <Title level={2} className="text-center mb-8">ChatGPT Plus 充值</Title>
          
          {/* 步骤指示器 */}
          <Steps 
            current={currentStep} 
            items={[
              { title: '检验卡密' },
              { title: '输入Cookies' },
              { title: '确认信息' },
              { title: '完成' },
            ]}
            className="mb-8"
          />
          
          {/* 步骤1: 检验卡密 */}
          {currentStep === 0 && (
            <div>
              <Title level={4} className="mb-4">步骤 1: 检验卡密</Title>
              <Form layout="vertical">
                <Form.Item label="请输入您的卡密">
                  <Input
                    placeholder="请输入您购买的卡密"
                    value={activationCode}
                    onChange={(e) => setActivationCode(e.target.value)}
                    onPressEnter={handleCheckCode}
                  />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" onClick={handleCheckCode} block loading={isCheckingCode} disabled={isCheckingCode}>
                    检验卡密
                  </Button>
                </Form.Item>
              </Form>
            </div>
          )}
          
          {/* 步骤2: 输入Cookies */}
          {currentStep === 1 && (
            <div>
              <Title level={4} className="mb-4">步骤 2: 输入 ChatGPT Cookies</Title>
              <Text type="secondary" className="mb-4 block">
                请按照以下步骤获取您的 ChatGPT Cookies:
              </Text>
              <ol className="list-decimal list-inside space-y-2 mb-6">
                <li>
                  登录您的 ChatGPT 账号，打开 <a href="https://chatgpt.com/api/auth/session" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    https://chatgpt.com/api/auth/session
                  </a> 。页面必须显示密密麻麻的字符，否则请重新登录。
                </li>
                <li>
                  使用浏览器插件（如 <a href="https://chromewebstore.google.com/detail/editthiscookie-v3/ojfebgpkimhlhcblbalbfjblapadhbol" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    EditThisCookie
                  </a>）来复制您的 cookies。
                  您可以通过 <a href="https://chromewebstore.google.com/detail/editthiscookie-v3/ojfebgpkimhlhcblbalbfjblapadhbol" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    这里
                  </a> 了解如何使用。
                </li>
              </ol>
              <Form layout="vertical">
                <Form.Item label="请输入您的 ChatGPT Cookies">
                  <TextArea
                    rows={6}
                    placeholder="请粘贴您从上述步骤中获取的 cookies"
                    value={cookies}
                    onChange={(e) => setCookies(e.target.value)}
                  />
                </Form.Item>
                <Space>
                  <Button onClick={handlePrev}>上一步</Button>
                  <Button type="primary" onClick={handleNextToConfirm}>
                    下一步
                  </Button>
                </Space>
              </Form>
            </div>
          )}
          
          {/* 步骤3: 确认信息 */}
          {currentStep === 2 && (
            <div>
              <Title level={4} className="mb-4">步骤 3: 确认信息</Title>
              <Card className="mb-6 bg-blue-50 border-blue-200">
                <Text strong>请仔细核对以下信息：</Text>
                <div className="mt-2">
                  <Text>卡密: </Text>
                  <Text code>{activationCode}</Text>
                </div>
                <div className="mt-2">
                  <Text>Cookies (前50个字符): </Text>
                  <Text code>{cookies.substring(0, 50)}{cookies.length > 50 ? '...' : ''}</Text>
                </div>
              </Card>
              
              <Form layout="vertical">
                <Form.Item>
                  <label>
                    <input
                      type="checkbox"
                      checked={isConfirmChecked}
                      onChange={(e) => setIsConfirmChecked(e.target.checked)}
                      className="mr-2"
                    />
                    我确认以上信息准确无误，并授权系统使用这些信息进行充值操作。
                  </label>
                </Form.Item>
                <Space>
                  <Button onClick={handlePrev}>上一步</Button>
                  <Button 
                    type="primary" 
                    onClick={handleSubmitOrder} 
                    loading={isSubmitting}
                    disabled={!isConfirmChecked || isSubmitting}
                  >
                    确定充值
                  </Button>
                </Space>
              </Form>
            </div>
          )}
          
          {/* 步骤4: 完成 */}
          {currentStep === 3 && (
            <div className="text-center">
              <Title level={3} className="text-green-600 mb-4">🎉 充值请求已提交</Title>
              <Text className="block mb-2">
                您的充值请求已成功提交，请耐心等待。通常情况下，充值将在一个小时内完成。
              </Text>
              <Text className="block mb-6">
                如果超过预期时间仍未完成，请联系客服微信获取帮助。
              </Text>
              <Button type="primary" onClick={handleGoHome}>
                返回首页
              </Button>
            </div>
          )}
          
          {/* 错误处理: 如果服务不可用 */}
          {currentStep === 4 && (
            <div className="text-center">
              <Title level={3} className="text-red-600 mb-4">❌ 服务暂时不可用</Title>
              <Text className="block mb-6">
                很抱歉，当前服务暂时不可用。请稍后再试，或联系客服微信获取帮助。
              </Text>
              <Button type="primary" onClick={handleGoHome}>
                返回首页
              </Button>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default RechargePlusPage;