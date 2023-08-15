// Generated using webpack-cli https://github.com/webpack/webpack-cli

const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const WorkboxWebpackPlugin = require("workbox-webpack-plugin");
const WebpackShellPluginNext = require('webpack-shell-plugin-next');
const CopyPlugin = require("copy-webpack-plugin");

const isProduction = process.env.NODE_ENV == "production";

const stylesHandler = isProduction
  ? MiniCssExtractPlugin.loader
  : "style-loader";

const config = {
  entry: "./src/index.js",
  output: {
    path: path.resolve(__dirname, "dist"),
  },
  devServer: {
    allowedHosts: 'auto',
    open: true,
    headers: {
      "Access-Control-Allow-Origin": "*"
    },
    proxy: {
      "/s3": {
        target: "https://letterfowl-test.s3.fr-par.scw.cloud",
        changeOrigin: true,
        pathRewrite: { "^/s3": "" }
      }
    }
  },
  plugins: [
    new WebpackShellPluginNext({
      onBuildStart: {
        scripts: [
          "cd .. && poetry build && cd app"
        ],
        blocking: true,
        parallel: false
      },
      swallowError: true
    }),
    new HtmlWebpackPlugin({
      template: "index.html",
    }),
    new CopyPlugin({
      patterns: [
        { from: "../dist/*", to: "." },
        { from: "../settings.toml", to: "." },
      ],
    }),
    // Add your plugins here
    // Learn more about plugins from https://webpack.js.org/configuration/plugins/
  ],
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/i,
        loader: "babel-loader",
      },
      {
        test: /\.css$/i,
        use: [stylesHandler, "css-loader"],
      },
      {
        test: /\.s[ac]ss$/i,
        use: [stylesHandler, "css-loader", "sass-loader"],
      },
      {
        test: /\.(eot|svg|ttf|woff|woff2|png|jpg|gif)$/i,
        type: "asset",
      },

      // Add your rules for custom modules here
      // Learn more about loaders from https://webpack.js.org/loaders/
    ],
  },
  externals: {
    pyodide: 'loadPyodide'
  },
  experiments: {
    asyncWebAssembly: true,
    topLevelAwait: true,
  },
  devtool: 'eval-source-map'
};

module.exports = () => {
  if (isProduction) {
    config.mode = "production";

    config.plugins.push(new MiniCssExtractPlugin());

    config.plugins.push(new WorkboxWebpackPlugin.GenerateSW());
  } else {
    config.mode = "development";
  }
  return config;
};
