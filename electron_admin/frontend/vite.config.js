import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

import path from 'path'
// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  return {
    // 项目插件
    plugins: [
      vue(),
    ],
    // 基础配置
    base: './',
    publicDir: 'public',
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
        'path': 'path-browserify'
      },
    },
    css: {
      preprocessorOptions: {
        less: {
          modifyVars: {
            '@border-color-base': '#dce3e8',
          },
          javascriptEnabled: true,
        },
      },
    },
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      assetsInlineLimit: 4096,
      cssCodeSplit: true,
      brotliSize: false,
      sourcemap: false,
      minify: 'terser',
      terserOptions: {
        compress: {
          // 生产环境去除console及debug
          drop_console: false,
          drop_debugger: true,
        },
      },
    },
    // 开发服务器配置
    server: {
      port: 8900,
      host: '0.0.0.0',
      open: false
      // 不再需要代理配置，所有请求通过网关统一管理
    }
  }
})


