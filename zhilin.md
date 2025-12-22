请帮我修改当前项目中的 index.html 文件，主要解决“缺少图标”、“导航栏样式”和“顶部间距”这三个问题。请按以下步骤执行修改：

1. **添加 Favicon (网页图标)**：
   在 `<head>` 标签内（`<title>` 下方）插入以下代码，使用 Data URI 格式的 SVG 图标：
   `<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>⚡</text></svg>">`

2. **优化字体显示**：
   在 `<style>` 标签内的 `body` 样式中，增加字体抗锯齿属性：
   `-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;`

3. **重构导航栏 (Navbar)**：
   - 找到 `<nav id="navbar">` 元素，将其 `class` 整体替换为：
     `fixed top-0 w-full z-50 transition-all duration-300 border-b border-transparent bg-transparent`
   - 将导航栏内部菜单链接 (`<a>` 标签) 的 `text-sm font-medium` 修改为 `text-[15px] font-semibold tracking-wide`，让字体更清晰。

4. **调整 Hero 区域间距**：
   找到页面第一个 `<section>` (Hero 部分)，将其 class 中的 `pt-32` 修改为 `pt-24`，减少顶部留白。

5. **更新底部 JS 滚动逻辑**：
   找到控制导航栏背景的 `<script>`，用以下代码替换原有的 `toggleNavBg` 逻辑，实现“顶部全透明，滚动变磨砂”的效果：
   ```javascript
   const navbar = document.getElementById('navbar');
   const toggleNavBg = () => {
       if (!navbar) return;
       if (window.scrollY > 20) {
           // 滚动后：深色毛玻璃背景
           navbar.classList.add('bg-[#020410]/80', 'backdrop-blur-xl', 'border-white/5');
           navbar.classList.remove('border-transparent', 'bg-transparent');
       } else {
           // 顶部时：完全透明
           navbar.classList.remove('bg-[#020410]/80', 'backdrop-blur-xl', 'border-white/5');
           navbar.classList.add('border-transparent', 'bg-transparent');
       }
   };
   toggleNavBg();
   window.addEventListener('scroll', toggleNavBg);