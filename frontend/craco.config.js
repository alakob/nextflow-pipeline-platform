module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Find the webpack-dev-server configuration
      const devServerConfigIndex = webpackConfig.plugins.findIndex(
        (plugin) => plugin.constructor.name === 'WebpackDevServerPlugin'
      );

      if (devServerConfigIndex !== -1) {
        // Remove deprecated options
        if (webpackConfig.plugins[devServerConfigIndex].options) {
          const options = webpackConfig.plugins[devServerConfigIndex].options;
          
          // Remove deprecated middleware options
          if (options.onBeforeSetupMiddleware) {
            delete options.onBeforeSetupMiddleware;
          }
          if (options.onAfterSetupMiddleware) {
            delete options.onAfterSetupMiddleware;
          }
          
          // Add the new setupMiddlewares option if needed
          if (!options.setupMiddlewares) {
            options.setupMiddlewares = (middlewares, devServer) => {
              return middlewares;
            };
          }
        }
      }
      
      return webpackConfig;
    },
  },
};
