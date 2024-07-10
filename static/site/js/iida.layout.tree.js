/* global cytoscape */

// 5 stage clos layout
(function () {

  if (!cytoscape) {
    return;
  }

  function iida_tree_layout(arguments) {
    this.options = arguments.options || {};
    this.cy = arguments.cy;
    this.eles = arguments.eles;
    const self = this;

    //
    // run() is called when layout is created
    //
    this.run = function() {

      const eles = this.eles;

      const root_id = this.options['root_id'];
      const root_node = root_id ? eles.getElementById(root_id) : eles.nodes().filter(node => is_root(node)).first();
      if (root_node === undefined) {
        console.error('root node is not found');
        return;
      }

      // set tree_parent, tree_children to each node
      eles.nodes().forEach(node => {
        node.data('tree_children', []);

        node.data('children').forEach(child_id => {
          let child_node = eles.getElementById(child_id);
          if (child_node) {
            // set pointer to parent as "tree_parent"
            child_node.data('tree_parent', node);

            // set pointer to children as "tree_children"
            node.data('tree_children').push(child_node);
          }
        });
      });

      // set y and depth
      calc_y_preorder(root_node);

      // set x and mod
      calc_x_postorder(root_node);

      // fix x
      calc_x_preorder(root_node);

      // cleanup
      eles.nodes().forEach(node => {
        node.removeData('tree_parent');
        node.removeData('tree_children');
      });

      // run the layout
      eles.nodes().layoutPositions(this, this.options, function (node, _index) {
        return { x: node.position().x, y: node.position().y };
      });

      // this.cy.fit();
      this.cy.center();

      return this;
    }

    // stop() is called when layout is stopped
    this.stop = function () {
      return this;
    }

    //
    // utility functions to handle tree structure
    //

    function is_leaf(node) {
      return node.data('tree_children').length === 0;
    }

    function is_root(node) {
      return node.data('tree_parent') === undefined;
    }

    function is_left_most(node) {
      if (is_root(node)) {
        return true;
      }
      const parent_node = node.data('tree_parent');
      return parent_node.data('children').at(0) === node.id();
    }

    function is_right_most(node) {
      if (is_root(node)) {
        return true;
      }
      const parent_node = node.data('tree_parent');
      return parent_node.data('children').at(-1) == node.id();
    }

    function get_previous_sibling(node) {
      if (is_root(node)) {
        return undefined;
      }
      const parent_node = node.data('tree_parent');
      const siblings = parent_node.data('tree_children');
      const index = siblings.indexOf(node);
      if (index === 0) {
        return undefined;
      }
      return siblings[index - 1];
    }

    function get_next_sibling(node) {
      if (is_root(node)) {
        return undefined;
      }
      const parent_node = node.data('tree_parent');
      const siblings = parent_node.data('tree_children');
      const index = siblings.indexOf(node);
      if (index === siblings.length - 1) {
        return undefined;
      }
      return siblings[index + 1];
    }

    function get_left_most_sibling(node) {
      if (is_root(node)) {
        return undefined;
      }
      const parent_node = node.data('tree_parent');
      return parent_node.data('tree_children').at(0);
    }

    function get_left_most_child(node) {
      if (is_leaf(node)) {
        return undefined;
      }
      return node.data('tree_children').at(0);
    }

    function get_right_most_child(node) {
      if (is_leaf(node)) {
        return undefined;
      }
      return node.data('tree_children').at(-1);
    }

    //
    // layout algorithm
    //

    function calc_y_preorder(node, depth=0) {
      if (node === undefined) {
        return;
      }

      // preorder process

      // set depth
      node.data('depth', depth);

      // set y
      if (is_root(node)) {
        node.data('y', 0);
      } else {
        const minimal_y_distance = self.options['minimal_y_distance'] || 100;
        const parent_node = node.data('tree_parent');
        node.data('y', parent_node.data('y') + minimal_y_distance);
      }

      // traverse children
      node.data('tree_children').forEach(child_node => {
        calc_y_preorder(child_node, depth + 1);
      });
    }


    function calc_x_postorder(node) {
      if (node === undefined) {
        return;
      }

      // traverse children
      node.data('tree_children').forEach(child_node => {
        calc_x_postorder(child_node);
      });

      // postorder process

      const minimal_x_distance = self.options['minimal_x_distance'] || 50;

      // in case of no child
      if (node.data('tree_children').length === 0) {
        if (is_left_most(node)) {
          node.data('x', 0);
        } else {
          const left_sibling = get_previous_sibling(node);
          node.data('x', left_sibling.data('x') + minimal_x_distance);
        }
        return;
      }

      // in case of 1 child
      if (node.data('tree_children').length === 1) {
        const child = node.data('tree_children').at(0);
        if (is_left_most(node)) {
          node.data('x', child.data('x'));
        } else {
          const left_sibling = get_previous_sibling(node);
          node.data('x', left_sibling.data('x') + minimal_x_distance);
          node.data('mod', node.data('x') - child.data('x'));
        }
      }
      // in case of 2 or more children
      else {
        const center_x = (get_left_most_child(node).data('x') + get_right_most_child(node).data('x')) / 2;
        if (is_left_most(node)) {
          node.data('x', center_x);
        } else {
          const left_sibling = get_previous_sibling(node);
          node.data('x', left_sibling.data('x') + minimal_x_distance);
          node.data('mod', node.data('x') - center_x);
        }
      }

      if (is_left_most(node)) {
        return;
      }

      resolve_overlap(node);

      if (is_right_most(node)) {
        equalize_position(node);
      }
    }


    function get_left_countour(node, mod_sum=0.0, left_countour={}) {
      if (node === undefined) {
        return;
      }

      // preorder traversal

      if (left_countour[node.data('depth')] === undefined) {
        left_countour[node.data('depth')] = node.data('x') + mod_sum;
      } else {
        left_countour[node.data('depth')] = Math.min(left_countour[node.data('depth')], node.data('x') + mod_sum);
      }

      mod_sum += node.data('mod');

      node.data('tree_children').forEach(child_node => {
        get_left_countour(child_node, mod_sum, left_countour);
      });
    }


    function get_right_contour(node, mod_sum=0.0, right_countour={}) {
      if (node === undefined) {
        return;
      }

      // preorder traversal

      if (right_countour[node.data('depth')] === undefined) {
        right_countour[node.data('depth')] = node.data('x') + mod_sum;
      } else {
        right_countour[node.data('depth')] = Math.max(right_countour[node.data('depth')], node.data('x') + mod_sum);
      }

      mod_sum += node.data('mod');

      node.data('tree_children').forEach(child_node => {
        get_right_contour(child_node, mod_sum, right_countour);
      });
    }


    function get_minimum_distance_between(left_node, right_node) {
      const left_node_right_countour = {};
      get_right_contour(left_node, 0.0, left_node_right_countour);

      const right_node_left_countour = {};
      get_left_countour(right_node, 0.0, right_node_left_countour);

      // change keys from string to integer
      const right_contour_depth_list = Object.keys(right_node_left_countour).map(s => parseInt(s));
      const left_contour_depth_list = Object.keys(left_node_right_countour).map(s => parseInt(s));

      // get minimum depth
      const min_depth = Math.min(Math.max(...right_contour_depth_list), Math.max(...left_contour_depth_list));

      let min_distance = Infinity;
      for (depth = right_node.data('depth') + 1; depth <= min_depth; depth++) {
        const distance = right_node_left_countour[depth] - left_node_right_countour[depth];
        min_distance = Math.min(min_distance, distance);
      }
      return min_distance;
    }


    function resolve_overlap(node) {
      const minimal_x_distance = self.options['minimal_x_distance'] || 50;

      let sibling = get_left_most_sibling(node);
      while (sibling !== undefined && sibling !== node) {
        let shift_value = 0;
        let distance = get_minimum_distance_between(sibling, node);
        if (distance + shift_value < minimal_x_distance) {
          shift_value = minimal_x_distance - distance;
        }
        if (shift_value > 0) {
          node.data('x', node.data('x') + shift_value);
          node.data('mod', node.data('mod') + shift_value);
        }

        sibling = get_next_sibling(sibling);
      }
    }


    function equalize_position(node) {
      const node_x = node.data('x');

      const minimal_x_distance = self.options['minimal_x_distance'] || 50;

      node_index = node.data('tree_parent').data('tree_children').indexOf(node);
      const num_nodes_between = node_index - 1;
      if (num_nodes_between <= 0) {
        return false;
      }

      const width = node.data('x') - get_left_most_sibling(node).data('x');
      const desired_interval = width / (num_nodes_between + 1);

      for (i = 1; i <= node_index; i++) {
        const mid_node = node.data('tree_parent').data('tree_children').at(i);
        const prev_node = node.data('tree_parent').data('tree_children').at(i - 1);
        if (i === 1) {
          // pass
        } else if (is_leaf(mid_node)) {
          // pass
        } else {
          const distance = get_minimum_distance_between(prev_node, mid_node);
          if (distance < minimal_x_distance) {
            const shift_value = minimal_x_distance - distance;
            mid_node.data('x', mid_node.data('x') + shift_value);
            mid_node.data('mod', mid_node.data('mod') + shift_value);
          }
        }

        if (mid_node.data('x') - prev_node.data('x') < desired_interval) {
          const shift_value = desired_interval - mid_node.data('x') + prev_node.data('x');
          mid_node.data('x', mid_node.data('x') + shift_value);
          mid_node.data('mod', mid_node.data('mod') + shift_value);
        }
      }

      if (node_x !== node.data('x')) {
        return true;
      }
      return false;
    }

    function calc_x_preorder(node, mod_sum=0.0) {
      if (node === undefined) {
        return;
      }

      // preorder process

      node.data('x', node.data('x') + mod_sum);

      mod_sum += node.data('mod');
      node.data('mod', 0);

      node.position({ x: node.data('x'), y: node.data('y') });
      node.data('initial_position', { x: node.data('x'), y: node.data('y') });

      node.data('tree_children').forEach(child_node => {
        calc_x_preorder(child_node, mod_sum);
      });
    }

  }

  // register layout extension to cytoscape
  cytoscape('layout', 'IIDA_TREE', iida_tree_layout);

})();