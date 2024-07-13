// define namespace `iida`
(function () {
  // the `this` means global
  // the `iida` is a object defined here
  this.iida = this.iida || (function () {

    // network diagram data locates under `appdata`
    let appdata = {};

    // this is the `iida` object
    return {
      'appdata': appdata
    };

  })();
})();


// define function iida.main()
(function () {
  iida.main = function () {

    Promise.all([
      // read json data via network
      fetch('data/test_tree_1.json', { mode: 'no-cors' })
        .then(response => {
          if (response.ok) {
            return response.json()
          }
          return [];
        })
        .catch(error => {
          console.error(error);
        }),
      fetch('data/test_tree_2.json', { mode: 'no-cors' })
        .then(response => {
          if (response.ok) {
            return response.json()
          }
          return [];
        })
        .catch(error => {
          console.error(error);
        }),
      fetch('data/test_tree_3.json', { mode: 'no-cors' })
        .then(response => {
          if (response.ok) {
            return response.json()
          }
          return [];
        })
        .catch(error => {
          console.error(error);
        }),
      fetch('data/test_tree_4.json', { mode: 'no-cors' })
        .then(response => {
          if (response.ok) {
            return response.json()
          }
          return [];
        })
        .catch(error => {
          console.error(error);
        })
    ]).then(function (dataArray) {
      iida.appdata.test_tree_1 = dataArray[0];
      iida.appdata.test_tree_2 = dataArray[1];
      iida.appdata.test_tree_3 = dataArray[2];
      iida.appdata.test_tree_4 = dataArray[3];

      // see, iida.nwdiagram.js
      iida.nwdiagram();
    });
  }

})();