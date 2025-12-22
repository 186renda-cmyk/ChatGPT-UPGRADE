export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // 路由映射表
    const map = {
      // 1. 共享号 (Pricing 左边卡片) -> 指向商品 ID 238
      "/go/gpt-shared": "https://www.naifeistation.com/index/buy?id=238&invite=3903",
      
      // 2. 独享号 (Pricing 右边卡片) -> 指向商品 ID 238 (与共享号同落地页)
      "/go/gpt-exclusive": "https://www.naifeistation.com/index/buy?id=238&invite=3903",
      
      // 3. 尊享代充 (Hero按钮 / Pricing 中间卡片) -> 指向商品 ID 241
      "/go/gpt-topup": "https://www.naifeistation.com/index/buy?id=241&invite=3903"
    };

    // 匹配并执行跳转 (302 临时重定向，方便以后随时改链接)
    if (map[url.pathname]) {
      return Response.redirect(map[url.pathname], 302);
    }
    
    // 如果不是跳转链接，则正常加载网页资源
    return env.ASSETS.fetch(request);
  }
};