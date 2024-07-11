/* global iida, cytoscape, document */

(function () {

  iida.nwdiagram = function () {

    if (!document.getElementById('cy')) {
      return;
    }

    let cy_styles = [

      {
        selector: ':parent',
        style: {
          'background-opacity': 0
        }
      },

      {
        selector: 'node',
        style: {
          'content': 'data(name)',
          'text-opacity': 1.0,
          'opacity': 1.0,
          'text-valign': 'center',
          'text-halign': 'center',
          'text-wrap': 'wrap',
          'font-size': '10px',
        }
      },

      {
        selector: 'edge',
        style: {
          'width': 1.6,
          'curve-style': "straight", // "bezier", "taxi" "bezier" "segments",
          'line-color': "#a9a9a9",  // darkgray
          // 'target-arrow-color': "#a9a9a9",  // darkgray
          // 'source-arrow-color': "#a9a9a9",  // darkgray
          // 'target-arrow-shape': "circle",
          // 'source-arrow-shape': "circle",
          // 'text-wrap': "wrap",  // wrap is needed to work '\n'
          // 'label': "data(label)",
          // 'label': edge => edge.data('label') ? `\u2060${edge.data('label')}\n\n\u2060` : '',
          // 'font-size': "10px",
          // 'edge-text-rotation': "autorotate"
          // 'source-text-offset': 10,
          // 'target-text-offset': 10,
          'z-index': 0
        }
      },
    ]

    let DEFAULT_LAYOUT_OPTIONS = {
      root_id: "root",
      horizontal: false,
      minimal_x_distance: 80,
      minimal_y_distance: 80,
    };

    const layout_options = {};
    Object.assign(layout_options, DEFAULT_LAYOUT_OPTIONS);

    cytoscape.warnings(false);
    let cy = window.cy = cytoscape({
      container: document.getElementById('cy'),
      minZoom: 0.5,
      maxZoom: 3,
      wheelSensitivity: 0.2,

      boxSelectionEnabled: false,
      autounselectify: true,
      hideEdgesOnViewport: false, // hide edges during dragging ?
      textureOnViewport: false,

      layout: {
        name: "IIDA_TREE", // see iida.layout.tree.js
        options: layout_options
      },
      // layout: { 'name': "preset" },

      style: cy_styles, // see above

      elements: iida.appdata.get_elements()
    });
    cytoscape.warnings(true);

    // add the panzoom control with default parameter
    // https://github.com/cytoscape/cytoscape.js-panzoom
    cy.panzoom({});

    function get_initial_position(node) {
      return node.data('initial_position');
    };

    function animate_to_initial_position() {
      Promise.all(cy.nodes().map(node => {
        return node.animation({
          position: get_initial_position(node),
          duration: 1000,
          easing: "ease"
        }).play().promise();
      }));
    };

    // the button to revert to initial position
    let button_initial_position = document.getElementById('idInitialPosition');
    if (button_initial_position) {
      button_initial_position.addEventListener('click', function (evt) {
        evt.stopPropagation();
        evt.preventDefault();
        animate_to_initial_position();
      });
    };

    // the button to dump elements JSON data to console
    let button_to_json = document.getElementById('idToJson');
    if (button_to_json) {
      button_to_json.addEventListener('click', function (evt) {
        evt.stopPropagation();
        evt.preventDefault();
        let elements_json = cy.elements().jsons();
        let elements_json_str = JSON.stringify(elements_json, null, 2);
        console.log(elements_json_str);
      });
    };

    ['idData1', 'idData2', 'idData3'].forEach(id => {
      let tag = document.getElementById(id);
      if (!tag) { return; }
      tag.addEventListener('click', function (evt) {
        evt.stopPropagation();
        evt.preventDefault();
        document.getElementsByName('dataChangeMenu').forEach(element => {
          element.classList.remove('active');
        });
        evt.target.classList.add('active');

        let tree_nodes;
        switch (id) {
          case 'idData1':
            tree_nodes = iida.appdata.test_tree_1;
            Object.assign(layout_options, { horizontal: false });
            break;
          case 'idData2':
            tree_nodes = iida.appdata.test_tree_2;
            Object.assign(layout_options, { horizontal: false, minimal_x_distance: 80, minimal_y_distance: 120 });
            break;
          case 'idData3':
            tree_nodes = iida.appdata.test_tree_3;
            Object.assign(layout_options, { horizontal: true, minimal_x_distance: 40, minimal_y_distance: 120 });
            break;
        }

        // remove all elements
        cy.elements().remove();

        // reset zoom etc
        cy.reset();

        // add new elements
        cy.add(iida.appdata.get_elements(tree_nodes));

        // layout again
        cy.layout({ name: "IIDA_TREE", options: layout_options }).run();
      });
    });

  };
  //
})();
