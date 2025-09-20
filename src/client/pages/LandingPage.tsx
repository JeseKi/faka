import React, { useEffect, useState, useRef } from 'react';

const wechatId = import.meta.env.VITE_WECHAT_ID;

const LandingPage: React.FC = () => {
  const [blogPanelOpen, setBlogPanelOpen] = useState(false);
  const blogPanelRef = useRef<HTMLDivElement>(null);
  const blogToggleRef = useRef<HTMLButtonElement>(null);
  const closeBlogRef = useRef<HTMLButtonElement>(null);
  const toggleArrowRef = useRef<HTMLSpanElement>(null);
  const darkModeToggleRef = useRef<HTMLButtonElement>(null);
  const darkModeIconRef = useRef<HTMLSpanElement>(null);
  const videoModalRef = useRef<HTMLDivElement>(null);
  const videoPlayerRef = useRef<HTMLVideoElement>(null);

  // 页面加载动画
  useEffect(() => {
    const sections = ['hero', 'reviews', 'steps', 'features', 'trust', 'usage', 'faq'];
    sections.forEach((id, index) => {
      const element = document.getElementById(id);
      if (element) {
        setTimeout(() => {
          element.classList.add('fade-in');
          (element as HTMLElement).style.opacity = '1';
        }, index * 200);
      }
    });
  }, []);

  // 事件追踪 (预留接口)
  const trackEvent = (eventName: string) => {
    // gtag('event', eventName);
    console.log('Event tracked:', eventName);
  };

  // 复制微信号功能
  const copyWechat = () => {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(wechatId).then(() => {
        showToast('微信号已复制到剪贴板！');
      }).catch(() => {
        fallbackCopy(wechatId);
      });
    } else {
      fallbackCopy(wechatId);
    }
  };

  // 降级复制方案
  const fallbackCopy = (text: string) => {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      showToast('微信号已复制到剪贴板！');
    } catch (err) {
      showToast('复制失败，请手动复制: ' + text);
      console.log(err)
    }
    document.body.removeChild(textArea);
  };

  // 简单提示框
  const showToast = (message: string) => {
    const toast = document.createElement('div');
    toast.className = 'fixed top-20 left-1/2 transform -translate-x-1/2 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transition-all duration-300';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }, 2000);
  };

  // 暗黑模式切换
  const toggleDarkMode = () => {
    document.documentElement.classList.toggle('dark');
    const isDark = document.documentElement.classList.contains('dark');
    if (darkModeIconRef.current) {
      darkModeIconRef.current.textContent = isDark ? '☀️' : '🌙';
    }
  };

  // 博客侧边栏功能
  const toggleBlogPanel = () => {
    setBlogPanelOpen(!blogPanelOpen);
  };

  const closeBlogPanel = () => {
    setBlogPanelOpen(false);
  };

  // 视频弹窗功能（懒加载优化）
  const openVideoModal = () => {
    if (videoModalRef.current && videoPlayerRef.current) {
      // 如果没有视频源，动态创建并加载
      if (!videoPlayerRef.current.querySelector('source')) {
        const source = document.createElement('source');
        source.src = 'https://tuchuang-1317479375.cos.ap-beijing.myqcloud.com/%E6%95%99%E7%A8%8B%E8%A7%86%E9%A2%91.mp4';
        source.type = 'video/mp4';
        videoPlayerRef.current.appendChild(source);
        
        // 加载视频
        videoPlayerRef.current.load();
      }
      
      videoModalRef.current.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
      videoPlayerRef.current.play().catch(error => {
        console.error("Video play failed:", error);
      });
    }
  };

  const closeVideoModal = () => {
    if (videoModalRef.current && videoPlayerRef.current) {
      videoModalRef.current.classList.add('hidden');
      document.body.style.overflow = '';
      videoPlayerRef.current.pause();
      videoPlayerRef.current.currentTime = 0;
    }
  };

  // 点击背景关闭弹窗
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (videoModalRef.current && event.target === videoModalRef.current) {
        closeVideoModal();
      }
    };

    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeVideoModal();
        closeBlogPanel();
      }
    };

    document.addEventListener('click', handleClickOutside);
    document.addEventListener('keydown', handleEscapeKey);

    return () => {
      document.removeEventListener('click', handleClickOutside);
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, []);

  // ESC键关闭面板
  useEffect(() => {
    const handleClickOutsideBlog = (event: MouseEvent) => {
      if (blogPanelRef.current && blogToggleRef.current) {
        if (!blogPanelRef.current.contains(event.target as Node) && 
            !blogToggleRef.current.contains(event.target as Node) && 
            blogPanelOpen) {
          closeBlogPanel();
        }
      }
    };

    document.addEventListener('click', handleClickOutsideBlog);

    return () => {
      document.removeEventListener('click', handleClickOutsideBlog);
    };
  }, [blogPanelOpen]);

  // 更新博客面板的类名
  useEffect(() => {
    if (blogPanelRef.current && toggleArrowRef.current) {
      if (blogPanelOpen) {
        blogPanelRef.current.classList.add('blog-panel-open');
        blogPanelRef.current.classList.remove('blog-panel-closed');
        toggleArrowRef.current.style.transform = 'rotate(180deg)';
      } else {
        blogPanelRef.current.classList.remove('blog-panel-open');
        blogPanelRef.current.classList.add('blog-panel-closed');
        toggleArrowRef.current.style.transform = 'rotate(0deg)';
      }
    }
  }, [blogPanelOpen]);

  return (
    <div className="font-sans bg-white text-gray-900 overflow-x-hidden">
      {/* Hero Section 首屏 */}
      <section className="min-h-screen flex items-center justify-center px-4 py-20 gradient-bg relative overflow-hidden">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="container mx-auto text-center relative z-10 opacity-0 fade-in" id="hero" style={{ opacity: 1 }}>
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight">
            ChatGPT Plus充值服务
            <span className="block text-3xl md:text-5xl font-light mt-2">国内用户首选的ChatGPT会员升级平台</span>
          </h1>
          {/* 信任徽章（响应式优化 - 网页端更大更醒目） */}
          <div className="flex flex-wrap justify-center gap-2 sm:gap-3 md:gap-4 mb-8">
            <span className="inline-flex items-center px-4 py-2 md:px-6 md:py-3 bg-gradient-to-r from-green-400 to-green-600 text-white text-sm md:text-base font-bold rounded-full border-2 border-white/30 shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300">
              <span className="mr-2 md:mr-3 text-lg md:text-xl">🔒</span>不封号
            </span>
            <span className="inline-flex items-center px-4 py-2 md:px-6 md:py-3 bg-gradient-to-r from-blue-400 to-blue-600 text-white text-sm md:text-base font-bold rounded-full border-2 border-white/30 shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300">
              <span className="mr-2 md:mr-3 text-lg md:text-xl">🛡️</span>不泄露账号
            </span>
            <span className="inline-flex items-center px-4 py-2 md:px-6 md:py-3 bg-gradient-to-r from-orange-400 to-orange-600 text-white text-sm md:text-base font-bold rounded-full border-2 border-white/30 shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300">
              <span className="mr-2 md:mr-3 text-lg md:text-xl">👥</span>50000+满意客户
            </span>
            <span className="inline-flex items-center px-4 py-2 md:px-6 md:py-3 bg-gradient-to-r from-purple-400 to-purple-600 text-white text-sm md:text-base font-bold rounded-full border-2 border-white/30 shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300">
              <span className="mr-2 md:mr-3 text-lg md:text-xl">✅</span>99.9%成功率
            </span>
            <span className="inline-flex items-center px-4 py-2 md:px-6 md:py-3 bg-gradient-to-r from-red-400 to-red-600 text-white text-sm md:text-base font-bold rounded-full border-2 border-white/30 shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300">
              <span className="mr-2 md:mr-3 text-lg md:text-xl">🕒</span>24/7小时在线客服
            </span>
          </div>
          
          <p className="text-xl md:text-2xl text-white/90 mb-8 font-light">
            20 秒完成充值，永久免费教程
          </p>
          
          {/* 主按钮组 */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <a href="/purchase" target="_blank" className="inline-flex items-center px-8 py-4 bg-white text-indigo-600 font-semibold rounded-2xl shadow-lg shadow-white/30 hover:shadow-white/50 hover:shadow-[0_0_30px_rgba(255,255,255,0.5)] hover:-translate-y-0.5 hover:scale-105 transition-all duration-300" onClick={() => trackEvent('purchase_click')}>
              <span>💎 购买卡密</span>
            </a>
            <a href="/recharge-plus" className="inline-flex items-center px-8 py-4 bg-transparent border-2 border-white text-white font-semibold rounded-2xl hover:bg-white hover:text-indigo-600 hover:-translate-y-0.5 transition-all duration-300" onClick={() => trackEvent('recharge_click')}>
              <span>⚡ 充值Plus</span>
            </a>
            <button onClick={openVideoModal} className="inline-flex items-center px-8 py-4 bg-transparent border-2 border-white text-white font-semibold rounded-2xl hover:bg-white hover:text-indigo-600 hover:-translate-y-0.5 transition-all duration-300">
              <span>📺 视频教程</span>
            </button>
          </div>
          
          {/* 价格对比 */}
          <div className="max-w-2xl mx-auto mb-12">
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              <div className="flex items-center justify-between p-4 border-b">
                <span className="text-lg font-semibold text-gray-900">充值方式</span>
                <span className="text-lg font-semibold text-gray-900">价格</span>
              </div>

              <div className="flex items-center justify-between p-6 bg-red-50 cursor-pointer hover:bg-red-100 hover:shadow-md hover:scale-[1.02] transition-all duration-300 group" onClick={() => window.open('/purchase', '_blank')}>
                <span className="text-gray-700">官方充值</span>
                <div className="flex items-center">
                  <span className="text-red-600 font-bold text-xl">¥158</span>
                  <span className="ml-2 text-red-400 group-hover:translate-x-1 transition-transform duration-300">→</span>
                </div>
              </div>
              <div className="flex items-center justify-between p-6 bg-blue-50 cursor-pointer hover:bg-blue-100 hover:shadow-md hover:scale-[1.02] transition-all duration-300 group" onClick={() => window.open('/purchase', '_blank')}>
                <span className="text-gray-700">新用户官方福利价</span>
                <div className="flex items-center">
                  <span className="text-blue-600 font-bold text-xl">¥140</span>
                  <span className="ml-2 text-blue-400 group-hover:translate-x-1 transition-transform duration-300">→</span>
                </div>
              </div>
              <div className="flex items-center justify-between p-6 bg-green-50 cursor-pointer hover:bg-green-100 hover:shadow-md hover:scale-[1.02] transition-all duration-300 group" onClick={() => window.open('/purchase', '_blank')}>
                <div className="flex items-center">
                  <span className="text-gray-700">三个月官方会员</span>
                  <span className="ml-2 px-2 py-1 bg-orange-100 text-orange-700 text-xs rounded-full font-medium">联系客服</span>
                </div>
                <div className="flex items-center">
                  <span className="text-green-600 font-bold text-xl">¥348</span>
                  <span className="ml-2 text-green-400 group-hover:translate-x-1 transition-transform duration-300">→</span>
                </div>
              </div>

            </div>
          </div>
        </div>
      </section>

      {/* 客户评价区域 */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="container mx-auto opacity-0 fade-in" id="reviews" style={{ opacity: 1 }}>
          <h2 className="text-4xl font-bold text-center mb-16 text-gray-900">客户真实评价</h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* 评价卡片1 - 纯图片展示 */}
            <div className="w-full">
              <img src="/images/image_1756607004003.png"
                   className="w-full h-auto object-contain rounded-lg"
                   alt="ChatGPT Plus充值客户好评截图 - 快速到账服务满意度高" loading="lazy" />
            </div>

            {/* 评价卡片2 - 纯图片展示 */}
            <div className="w-full">
              <img src="/images/image_1756607013801.png"
                   className="w-full h-auto object-contain rounded-lg"
                   alt="ChatGPT会员代充成功案例 - 20秒完成充值客户反馈" loading="lazy" />
            </div>

            {/* 评价卡片3 - 纯图片展示 */}
            <div className="w-full">
              <img src="/images/image_1756607018341.png"
                   className="w-full h-auto object-contain rounded-lg"
                   alt="ChatGPT充值服务用户推荐 - 安全可靠官方渠道" loading="lazy" />
            </div>
          </div>
        </div>
      </section>

      {/* Steps Section 流程说明 */}
      <section className="py-20 px-4 bg-white">
        <div className="container mx-auto opacity-0 fade-in" id="steps" style={{ opacity: 1 }}>
          <h2 className="text-4xl font-bold text-center mb-16 text-gray-900">ChatGPT Plus充值三步完成</h2>
          <div className="flex flex-col md:flex-row items-center justify-center gap-8">
            <div className="text-center">
              <div className="w-20 h-20 bg-indigo-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mb-4 mx-auto">1</div>
              <h3 className="text-xl font-semibold mb-2">第一步：点击购买卡密</h3>
              <p className="text-gray-600">选择套餐完成付款</p>
            </div>
            <div className="hidden md:block w-20 h-1 bg-gradient-to-r from-indigo-600 to-teal-500 rounded"></div>
            <div className="text-center">
              <div className="w-20 h-20 bg-teal-500 text-white rounded-full flex items-center justify-center text-2xl font-bold mb-4 mx-auto">2</div>
              <h3 className="text-xl font-semibold mb-2">第二步：登录ChatGPT账号</h3>
              <p className="text-gray-600">登录您的 ChatGPT 账号</p>
            </div>
            <div className="hidden md:block w-20 h-1 bg-gradient-to-r from-teal-500 to-green-500 rounded"></div>
            <div className="text-center">
              <div className="w-20 h-20 bg-green-500 text-white rounded-full flex items-center justify-center text-2xl font-bold mb-4 mx-auto">3</div>
              <h3 className="text-xl font-semibold mb-2">第三步：激活Plus会员</h3>
              <p className="text-gray-600">Plus 权限立即生效</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section 特性介绍 */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="container mx-auto opacity-0 fade-in" id="features" style={{ opacity: 1 }}>
          <h2 className="text-4xl font-bold text-center mb-16 text-gray-900">为什么选择我们的ChatGPT代充服务？</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-8 bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300">
              <div className="w-16 h-16 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl">🚀</span>
              </div>
              <h3 className="text-xl font-semibold mb-4">官方iOS正规代充通道</h3>
              <p className="text-gray-600">使用官方正规渠道，安全可靠不封号</p>
            </div>
            <div className="text-center p-8 bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl">💰</span>
              </div>
              <h3 className="text-xl font-semibold mb-4">2快速完成充值</h3>
              <p className="text-gray-600">全自动化系统，瞬间到账无需等待</p>
            </div>
            <div className="text-center p-8 bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300">
              <div className="w-16 h-16 bg-gradient-to-r from-orange-400 to-red-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl">🔐</span>
              </div>
              <h3 className="text-xl font-semibold mb-4">价格比官方便宜15%</h3>
              <p className="text-gray-600">优惠价格，让您享受最高性价比</p>
            </div>
          </div>
        </div>
      </section>

      {/* 信任保障区域 */}
      <section className="py-16 px-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-y border-blue-100">
        <div className="container mx-auto opacity-0 fade-in" id="trust" style={{ opacity: 1 }}>
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">🛡️ 信任保障</h2>
              <p className="text-lg text-gray-600">正规代充服务，全自动化充值技术</p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-8 mb-8">
              {/* 左侧：正规服务说明 */}
              <div className="bg-white rounded-2xl p-8 shadow-lg">
                <div className="flex items-center mb-6">
                  <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mr-4">
                    <span className="text-white text-xl">📱</span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">iOS 正规代充</h3>
                </div>
                <ul className="space-y-3 text-gray-600">
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    正规 Apple 账户充值通道
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    全自动化充值技术，无需人工干预
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    账户安全有保障，不留后门
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    7x24小时自动处理订单
                  </li>
                </ul>
              </div>
              
              {/* 右侧：客服联系 */}
              <div className="bg-white rounded-2xl p-8 shadow-lg">
                <div className="flex items-center mb-6">
                  <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mr-4">
                    <span className="text-white text-xl">💬</span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">遇到问题？</h3>
                </div>
                <div className="space-y-4">
                  <div className="p-4 bg-green-50 rounded-xl border border-green-200">
                    <p className="text-gray-700 mb-2">专属客服微信：</p>
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-lg font-semibold text-green-700">{wechatId}</span>
                      <button onClick={copyWechat} className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm">
                        复制微信号
                      </button>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500 bg-gray-50 p-3 rounded-lg">
                    <p>💡 温馨提示：已添加过 <span className="font-mono">{wechatId}</span> 的用户无需重复添加</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      

      {/* 使用说明区域 */}
      <section className="py-20 px-4 bg-white">
        <div className="container mx-auto opacity-0 fade-in" id="usage" style={{ opacity: 1 }}>
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">💡 使用说明</h2>
              <p className="text-lg text-gray-600">简单两步，快速完成充值</p>
            </div>
            
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 border border-blue-100">
                <div className="space-y-4 text-gray-700">
                  <div className="flex items-start">
                    <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-1">1</div>
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">发卡网自助购买卡密</h3>
                      <p className="text-gray-600">通过发卡网平台自助购买充值卡密，操作简单快捷</p>
                      <p className="text-sm text-blue-600 mt-2">💰 有需要代理价的请联系管理员微信获取优惠</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-1">2</div>
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">打开 gptplus.biz 进行充值</h3>
                      <p className="text-gray-600">访问充值网站，按照页面提示完成充值操作</p>
                      <p className="text-sm text-green-600 mt-2">📺 可以结合上方视频教程一步步操作</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* 代理联系提示 */}
              <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-2xl p-6 border border-yellow-200 text-center">
                <div className="flex items-center justify-center text-gray-700">
                  <span className="mr-2 text-2xl">👥</span>
                  <span className="font-semibold text-lg">需要代理价优惠？</span>
                  <span className="mx-3 text-orange-500">→</span>
                  <span className="font-mono bg-orange-100 px-4 py-2 rounded-lg text-orange-700 font-semibold">微信: {wechatId}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ常见问题部分 */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="container mx-auto opacity-0 fade-in" id="faq" style={{ opacity: 1 }}>
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">💡 常见问题解答(FAQ)</h2>
              <p className="text-lg text-gray-600">解答您关于ChatGPT Plus充值的所有疑问</p>
            </div>

            <div className="space-y-6">
              {/* FAQ 1 */}
              <div className="bg-white rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">❓ ChatGPT Plus充值需要多长时间？</h3>
                <p className="text-gray-600">通常在卡密后一小时内即可完成充值，Plus权限立即生效。我们使用人工进行亲自充值，比机器充值更可靠！</p>
              </div>

              {/* FAQ 2 */}
              <div className="bg-white rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">🔒 ChatGPT充值安全吗？会不会封号？</h3>
                <p className="text-gray-600">完全安全。我们使用官方正规代充通道，不会触碰您的账号密码，不会导致封号。已服务50000+用户无一例封号，安全记录完美。</p>
              </div>

              {/* FAQ 3 */}
              <div className="bg-white rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">💳 支持哪些支付方式？</h3>
                <p className="text-gray-600">支持支付宝、微信支付等国内主流支付方式，方便快捷。发卡网平台支持多种安全支付渠道，确保交易安全。</p>
              </div>

              {/* FAQ 4 */}
              <div className="bg-white rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">❌ 充值失败怎么办？</h3>
                <p className="text-gray-600">如果充值失败，请联系客服微信：{wechatId}，我们提供24小时客服支持，会立即为您处理并保证充值成功。</p>
              </div>

              {/* FAQ 5 */}
              <div className="bg-white rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">🆚 ChatGPT Plus和免费版有什么区别？</h3>
                <p className="text-gray-600">ChatGPT Plus提供GPT-4访问权限、更快的响应速度、优先使用权和更稳定的服务。免费版只能使用GPT-3.5，且有使用限制。</p>
              </div>

              {/* FAQ 6 */}
              <div className="bg-white rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">🔄 可以给别人的ChatGPT账号充值吗？</h3>
                <p className="text-gray-600">可以。您只需要提供要充值的ChatGPT账号邮箱，我们就能为该账号充值Plus会员。操作简单，安全可靠。</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer 底部 */}
      <footer className="bg-gray-900 text-white py-12 px-4">
        <div className="container mx-auto text-center">
          <h3 className="text-2xl font-bold mb-4">GPT Plus 充值服务</h3>
          <p className="text-gray-400 mb-6">安全 · 快速 · 省钱</p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-8">
            <div className="flex items-center justify-center text-gray-400">
              <span className="mr-2">💬</span>
              <span>客服微信: {wechatId}</span>
            </div>
            <div className="flex items-center justify-center text-gray-400">
              <span className="mr-2">📱</span>
              <span>正规代充服务</span>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-6">
            <p className="text-gray-500 text-sm">
              © 2024 GPT Plus 充值服务. 本站仅提供技术服务，与 OpenAI 无关联关系。
            </p>
          </div>
        </div>
      </footer>

      {/* 博客侧边栏 */}
      <div className="fixed bottom-20 right-6 z-40" id="blogSidebar">
        {/* 博客标签按钮 */}
        <div className="flex justify-end mb-3">
          <button ref={blogToggleRef} onClick={toggleBlogPanel} className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-4 py-2 rounded-l-full shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 font-medium text-sm flex items-center space-x-2">
            <span>📖 博客推荐</span>
            <span ref={toggleArrowRef} className="transition-transform duration-300">◀</span>
          </button>
        </div>

        {/* 博客内容面板 */}
        <div ref={blogPanelRef} id="blogPanel" className="bg-white/95 backdrop-blur-md rounded-l-xl shadow-2xl p-4 w-80 sm:w-72 md:w-80 transform transition-all duration-300 border border-white/20 blog-panel-closed">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-800 flex items-center">
              <span className="mr-2">📚</span>
              推荐阅读
            </h3>
            <button ref={closeBlogRef} onClick={closeBlogPanel} className="text-gray-500 hover:text-gray-700 text-xl">×</button>
          </div>

          {/* 博客文章列表 */}
          <div className="space-y-3">
            <div className="blog-article-card flex items-start space-x-3 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border-l-4 border-blue-500 hover:shadow-md transition-all duration-200 cursor-pointer" onClick={() => window.open('/blog/chatgpt-plus-guide.html', '_blank')}>
              <span className="text-2xl flex-shrink-0 mt-1">📚</span>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-blue-600 font-medium bg-blue-100 px-2 py-1 rounded-full">使用指南</span>
                  <span className="text-xs text-gray-500">Hot</span>
                </div>
                <h4 className="text-sm font-semibold text-gray-800 mb-1 line-clamp-2">ChatGPT Plus完整使用指南：从入门到精通</h4>
                <p className="text-xs text-gray-600 line-clamp-2">详细介绍ChatGPT Plus的所有功能特性，包括GPT-4模型使用、插件功能...</p>
              </div>
            </div>

            <div className="blog-article-card flex items-start space-x-3 p-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border-l-4 border-purple-500 hover:shadow-md transition-all duration-200 cursor-pointer" onClick={() => window.open('/blog/chatgpt-plus-vs-pro.html', '_blank')}>
              <span className="text-2xl flex-shrink-0 mt-1">⚖️</span>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-purple-600 font-medium bg-purple-100 px-2 py-1 rounded-full">产品对比</span>
                  <span className="text-xs text-gray-500">New</span>
                </div>
                <h4 className="text-sm font-semibold text-gray-800 mb-1 line-clamp-2">ChatGPT Plus与ChatGPT Pro全面对比分析</h4>
                <p className="text-xs text-gray-600 line-clamp-2">深入对比ChatGPT Plus和Pro版本的功能差异、性能表现...</p>
              </div>
            </div>

            <div className="blog-article-card flex items-start space-x-3 p-3 bg-gradient-to-r from-red-50 to-yellow-50 rounded-lg border-l-4 border-red-500 hover:shadow-md transition-all duration-200 cursor-pointer" onClick={() => window.open('/blog/how-to-get-chatgpt-cookies.html', '_blank')}>
              <span className="text-2xl flex-shrink-0 mt-1">🍪</span>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-red-600 font-medium bg-red-100 px-2 py-1 rounded-full">技术教程</span>
                  <span className="text-xs text-gray-500">New</span>
                </div>
                <h4 className="text-sm font-semibold text-gray-800 mb-1 line-clamp-2">如何获取ChatGPT Cookies完整教程</h4>
                <p className="text-xs text-gray-600 line-clamp-2">详细教程：如何通过浏览器插件获取ChatGPT Cookies，用于API调用或自动化操作...</p>
              </div>
            </div>
          </div>

          {/* 查看更多按钮 */}
          <div className="mt-4 pt-3 border-t border-gray-200">
            <a href="/blog/index.html" className="block w-full text-center py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg font-medium text-sm hover:shadow-lg transition-all duration-300">
              查看全部文章 →
            </a>
          </div>
        </div>
      </div>

      {/* 客服悬浮按钮 */}
      <div className="fixed bottom-6 right-6 z-50">
        <a href="" className="w-14 h-14 bg-gradient-to-r from-indigo-600 to-teal-500 text-white rounded-full flex items-center justify-center shadow-lg hover:shadow-xl hover:scale-110 transition-all duration-300">
          <span className="text-xl">💬</span>
        </a>
      </div>

      
      {/* 暗黑模式切换按钮 */}
      <div className="fixed top-6 left-6 z-50">
        <button ref={darkModeToggleRef} onClick={toggleDarkMode} className="w-12 h-12 bg-white/20 backdrop-blur-sm text-white rounded-full flex items-center justify-center hover:bg-white/30 transition-all duration-300">
          <span ref={darkModeIconRef}>🌙</span>
        </button>
      </div>

      {/* 视频教程弹窗 */}
      <div ref={videoModalRef} id="videoModal" className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden">
        <div className="flex items-center justify-center h-full p-4">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden relative">
            <button onClick={closeVideoModal} className="absolute top-4 right-4 z-10 w-10 h-10 bg-black/50 text-white rounded-full flex items-center justify-center hover:bg-black/70 transition-colors">
              ✕
            </button>
            <video ref={videoPlayerRef} className="w-full" controls>
              {/* 视频源将在点击时动态加载 */}
              您的浏览器不支持视频播放
            </video>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;