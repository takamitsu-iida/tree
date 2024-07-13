/* global iida */

(function () {

  let DEFAULT_NODE_WIDTH = 40;
  let DEFAULT_NODE_HEIGHT = 40;

  // public function to get cytoscape.js elements
  iida.appdata.get_elements = function (tree_nodes) {

    tree_nodes = tree_nodes || iida.appdata.test_tree_1;

    // array to store cytoscape.js elements
    let eles = []

    tree_nodes.forEach(node => {
      if (node.group === 'edges') {
        return;
      }

      if ('id' in node.data === false) {
        return;
      }

      node.group = node.group || 'nodes';
      node.position = node.position || { x: 0, y: 0 };
      node.classes = node.classes || [];
      node.grabbable = node.grabbable || true;

      node.data.label = node.data.label || node.data.id;
      node.data.width = node.data.width || DEFAULT_NODE_WIDTH;
      node.data.height = node.data.height || DEFAULT_NODE_HEIGHT;
      node.data.children = node.data.children || [];
      node.data.depth = 0;
      node.data.x = 0;
      node.data.y = 0;
      node.data.mod = 0;

      node.data.children.forEach(child_id => {

        let edge = {
          group: 'edges',
          data: {
            'id': node.data.id + '-' + child_id,
            'source': node.data.id,
            'target': child_id,
            'control_point_distances': "0 0"
          }
        };

        eles.push(edge);
      });

      eles.push(node);
    });

    return eles;
  };

})();
