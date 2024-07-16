/* global cytoscape */

//
// iida_tree_layout
//
(function () {

  if (!cytoscape) {
    return;
  }

  function iida_tree_layout(arguments) {

    const self = this;

    this.options = arguments.options || {};
    this.cy = arguments.cy;
    this.eles = arguments.eles;

    //
    // run() is called when layout is created
    //
    this.run = function() {

      const root_id = this.options['root_id'];
      const root_node = root_id ? this.eles.getElementById(root_id) : this.eles.nodes().filter(node => is_root(node)).first();
      if (root_node === undefined) {
        console.error('root node is not found');
        return;
      }

      // set 'tree_parent' and 'tree_children' to each node
      this.eles.nodes().forEach(node => {
        node.data('tree_children', []);

        node.data('children').forEach(child_id => {
          let child_node = this.eles.getElementById(child_id);
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

      // set subtree info to drag subtree
      cy_set_subtree_postorder(root_node);

      // add cytoscape event handler
      cy_add_event_handler();

      // cleanup
      this.eles.nodes().forEach(node => {
        node.removeData('tree_parent');
        node.removeData('tree_children');
      });

      // run the layout
      this.eles.nodes().layoutPositions(this, this.options, function (node, _index) {
        if (self.options['horizontal'] === true) {
          node.position({ x: node.data('y'), y: node.data('x') });
          node.data('initial_position', { x: node.data('y'), y: node.data('x') });
          return node.position();
        }
        node.position({ x: node.data('x'), y: node.data('y') });
        node.data('initial_position', { x: node.data('x'), y: node.data('y') });
        return node.position();
      });

      // set edge bezier parameter
      this.eles.edges().forEach(edge => set_control_point_distances(edge));

      // this.cy.fit();
      this.cy.center();

      return this;
    }

    //
    // stop() is called when layout is stopped
    //
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

      // left_contour {
      //   key: tree depth,
      //   value: x position
      // }

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

      // get minimum distance between two subtrees
      const distance_list = [];
      for (depth = right_node.data('depth') + 1; depth <= min_depth; depth++) {
        const distance = right_node_left_countour[depth] - left_node_right_countour[depth];
        distance_list.push(distance);
      }
      return Math.min(...distance_list);
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

      // x = x + mod_sum
      node.data('x', node.data('x') + mod_sum);

      // mod_sum = mod_sum + mod
      mod_sum += node.data('mod');

      // clear mod
      node.data('mod', 0);

      // set position
      node.position({ x: node.data('x'), y: node.data('y') });

      // set initial_position
      node.data('initial_position', { x: node.data('x'), y: node.data('y') });

      // traverse children
      node.data('tree_children').forEach(child_node => {
        calc_x_preorder(child_node, mod_sum);
      });
    }

    //
    // cytoscape.js specific functions
    //

    function cy_set_subtree_postorder(node) {
      if (node === undefined) {
        return;
      }

      node.data('tree_children').forEach(child_node => {
        cy_set_subtree_postorder(child_node);
      });

      // postorder process

      node.data('subtree', []);

      if (is_leaf(node)) {
        return;
      }

      node.data('tree_children').forEach(child_node => {
        node.data('subtree').push(child_node.id());
        node.data('subtree').push(...child_node.data('subtree'));
      });
    }

    function cy_add_event_handler() {

      self.cy.nodes().on('grab', function (evt) {
        // save position at the moment of grab
        self.cy.nodes().forEach(function (node) {
          node.data('grabbed_position', { x: node.position().x, y: node.position().y });
        });
      });

      self.cy.nodes().on('drag', function (evt) {
        // restore grabbed position
        let grabbed_position = evt.target.data('grabbed_position');
        if (!grabbed_position) {
          return;
        }

        let delta_x = evt.target.position().x - grabbed_position.x;
        let delta_y = evt.target.position().y - grabbed_position.y;

        let drag_with_targets = evt.target.data('subtree') || [];
        drag_with_targets.forEach(function (drag_target) {
          let node = self.cy.getElementById(drag_target);
          if (!node || node === evt.target) {
            return;
          }
          node.position({ x: node.data('grabbed_position').x + delta_x, y: node.data('grabbed_position').y + delta_y });
        });

        // set edge bezier parameter
        const edges = evt.target.connectedEdges();
        edges.forEach(edge => {
          set_control_point_distances(edge);
        });

      });

    }


    function set_control_point_distances(edge) {

      if (self.options['horizontal'] === true) {
        //           target
        //           o
        //          /*
        //        */
        // source o
        //        *\
        //          \*
        //           o
        //           target

        const edge_vertical_length = edge.source().renderedPosition().y - edge.target().renderedPosition().y;
        const decrease_factor = 0.1;
        const control_point_distance = edge_vertical_length * decrease_factor;
        const control_point_distances = [control_point_distance, -1 * control_point_distance];
        edge.data('control_point_distances', control_point_distances.join(' '));
      } else {
        //    source    source
        //    o         o
        //  */           \*
        //  /*           *\
        // o               o
        // target          target

        const edge_holizontal_length = edge.source().renderedPosition().x - edge.target().renderedPosition().x;
        const decrease_factor = 0.1;
        const control_point_distance = edge_holizontal_length * decrease_factor;
        const control_point_distances = [-1 * control_point_distance, control_point_distance];
        edge.data('control_point_distances', control_point_distances.join(' '));
      }
    }

  }

  // register layout extension to cytoscape
  cytoscape('layout', 'IIDA_TREE', iida_tree_layout);

})();