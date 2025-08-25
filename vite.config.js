import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import { analyzer } from 'vite-bundle-analyzer'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  const isProduction = mode === 'production'
  const isDevelopment = mode === 'development'
  
  return {
    plugins: [
      react({
        // Enable Fast Refresh
        fastRefresh: isDevelopment,
        // Include emotion babel plugin for better performance
        babel: {
          plugins: [
            isDevelopment && require.resolve('react-refresh/babel')
          ].filter(Boolean)
        }
      }),
      
      // PWA Configuration
      VitePWA({
        registerType: 'prompt',
        includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
        manifest: {
          name: 'AI App Builder Pro',
          short_name: 'AppBuilderPro',
          description: 'AI-powered fullstack application builder with multi-agent system',
          theme_color: '#3B82F6',
          background_color: '#1F2937',
          display: 'standalone',
          start_url: '/',
          icons: [
            {
              src: 'pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png'
            },
            {
              src: 'pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png'
            },
            {
              src: 'pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'any maskable'
            }
          ]
        },
        workbox: {
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/api\./i,
              handler: 'NetworkFirst',
              options: {
                cacheName: 'api-cache',
                expiration: {
                  maxEntries: 50,
                  maxAgeSeconds: 300
                },
                cacheableResponse: {
                  statuses: [0, 200]
                }
              }
            }
          ]
        }
      }),
      
      // Bundle analyzer (only in analyze mode)
      process.env.ANALYZE && analyzer({
        analyzerMode: 'server',
        analyzerPort: 8888,
        openAnalyzer: true
      })
    ].filter(Boolean),

    // Path resolution
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@components': path.resolve(__dirname, './src/components'),
        '@lib': path.resolve(__dirname, './src/lib'),
        '@services': path.resolve(__dirname, './src/services'),
        '@utils': path.resolve(__dirname, './src/utils'),
        '@hooks': path.resolve(__dirname, './src/hooks'),
        '@types': path.resolve(__dirname, './src/types'),
        '@assets': path.resolve(__dirname, './src/assets')
      }
    },

    // CSS Configuration
    css: {
      postcss: {
        plugins: [
          require('tailwindcss'),
          require('autoprefixer')
        ]
      },
      devSourcemap: isDevelopment
    },

    // Development server configuration
    server: {
      host: true,
      port: 5173,
      strictPort: false,
      open: isDevelopment,
      cors: true,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:5000',
          changeOrigin: true,
          secure: false,
          timeout: 60000,
          configure: (proxy, _options) => {
            proxy.on('error', (err, _req, _res) => {
              console.log('Proxy error:', err)
            })
            proxy.on('proxyReq', (proxyReq, req, _res) => {
              console.log('Sending Request to the Target:', req.method, req.url)
            })
            proxy.on('proxyRes', (proxyRes, req, _res) => {
              console.log('Received Response from the Target:', proxyRes.statusCode, req.url)
            })
          }
        },
        '/socket.io': {
          target: env.VITE_API_URL || 'http://localhost:5000',
          changeOrigin: true,
          secure: false,
          ws: true,
          rewriteWsOrigin: true
        }
      }
    },

    // Preview configuration
    preview: {
      port: 4173,
      host: true,
      strictPort: true,
      open: true
    },

    // Build configuration
    build: {
      target: 'es2020',
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: !isProduction,
      minify: isProduction ? 'esbuild' : false,
      cssCodeSplit: true,
      reportCompressedSize: isProduction,
      
      // Rollup options
      rollupOptions: {
        input: {
          main: path.resolve(__dirname, 'index.html')
        },
        output: {
          manualChunks: {
            // Vendor chunk for React and related libraries
            react: ['react', 'react-dom', 'react-router-dom'],
            // UI library chunk
            ui: ['lucide-react', '@headlessui/react', '@heroicons/react', 'framer-motion'],
            // Utilities chunk
            utils: ['axios', 'socket.io-client', 'clsx', 'tailwind-merge', 'date-fns', 'lodash-es'],
            // Form handling chunk
            forms: ['react-hook-form', '@hookform/resolvers', 'zod']
          },
          chunkFileNames: 'assets/[name]-[hash].js',
          entryFileNames: 'assets/[name]-[hash].js',
          assetFileNames: 'assets/[name]-[hash].[ext]'
        }
      },

      // Build optimizations
      chunkSizeWarningLimit: 1000,
      
      // Terser options for production
      ...(isProduction && {
        terserOptions: {
          compress: {
            drop_console: true,
            drop_debugger: true
          }
        }
      })
    },

    // Environment variables
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
      __BUILD_DATE__: JSON.stringify(new Date().toISOString()),
      __DEV__: JSON.stringify(isDevelopment)
    },

    // Dependency optimization
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        'socket.io-client',
        'axios',
        'lucide-react',
        'framer-motion',
        '@headlessui/react',
        'clsx',
        'tailwind-merge'
      ],
      exclude: ['@vite/client', '@vite/env']
    },

    // ESBuild configuration
    esbuild: {
      target: 'es2020',
      logOverride: { 'this-is-undefined-in-esm': 'silent' }
    },

    // Worker configuration
    worker: {
      format: 'es'
    }
  }
})
