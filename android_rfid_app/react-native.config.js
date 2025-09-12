module.exports = {
  dependencies: {
    'react-native-tcp-socket': {
      platforms: {
        android: {
          sourceDir: '../node_modules/react-native-tcp-socket/android',
          packageImportPath: 'io.xogus.reactnative.tcpsocket.TcpSocketPackage',
        },
      },
    },
  },
};