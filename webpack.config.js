let webpack = require('webpack')
let path = require('path')
const VueLoaderPlugin = require('vue-loader/lib/plugin')



module.exports = {
    entry: './app/resources/js/app.js',

    mode: 'development',

    module: {
        rules: [
          {
            test: /\.vue$/,
            loader: 'vue-loader'
          },
          {
            test: /\.css$/,
            use: ['style-loader', 'css-loader']
          }
        ]
    },
    plugins: [
      new VueLoaderPlugin()
    ],

    output: {
        path: path.resolve(__dirname, './app/static/js/'),
        filename: 'bundle.js',
    }
    
}