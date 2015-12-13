var path = require('path');
var webpack = require("webpack");

module.exports = {
    context: path.join(__dirname, 'python_dashing', 'server', 'static', 'js'),
    entry: [
      "./app.js"
    ],
    output: {
        path: path.join(__dirname, 'python_dashing', 'server', 'static', 'js-build'),
        filename: "bundle.js",
        library: 'main',
    },
    module: {
        loaders: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                loader: 'babel',
                query: {
                    presets: ['react', 'es2015'],
                }
            },
        ]
    },
    plugins: [
      new webpack.NoErrorsPlugin()
    ]
};
