using Gtk;
using GLib;
using OpenIso.Core;

namespace OpenIso.UI {
        public class PipesExplorer : TreeView {

            /* = Variables = */
            private TreeView pipes_explorer;
            //private TreeStore pipes_store;
            private TreeIter world_level;
		    private TreeIter pipe_level;
		    //private TreeIter component_level;



            /* = Constructor = */
            public PipesExplorer (Array <Piping.Pipe> pipes_array) {

                /* Setting of TreeView */
                /* Show Tree Lines */
                this.enable_tree_lines = true;

                var pipes_store = new TreeStore (1, typeof (string));
		        pipes_explorer.set_model (pipes_store);
		        pipes_explorer.insert_column_with_attributes (-1, "Pipe Explorer", new CellRendererText (), "text", 0, null);

		        pipes_store.append (out world_level, null);
		        pipes_store.set (world_level, 0, "/*", -1);
			    for (int i = 0; i < pipes_array.length; i++) {
    				pipes_store.append (out pipe_level, world_level);
    				pipes_store.set (pipe_level, 0, pipes_array.index(i).Name, -1);
					//for (int j = 0; j < pipes_array.index(i).Components.length; j++){
                    //	pipes_store.set (product_iter, 0, pipes_array.index(i).Components.index(j).Name, -1);
                    //}

				//pipes_store.append (out product_iter, category_iter);
				//pipes_store.set (product_iter, 0, "Moby Dick", 1, "$10.36", -1);
				//pipes_store.append (out product_iter, category_iter);
				//pipes_store.set (product_iter, 0, "Heart of Darkness", 1, "$4.99", -1);
				//pipes_store.append (out product_iter, category_iter);
				//pipes_store.set (product_iter, 0, "Ulysses", 1, "$26.09", -1);
				//pipes_store.append (out product_iter, category_iter);
				//pipes_store.set (product_iter, 0, "Effective Vala", 1, "$38.99", -1);

				//pipes_store.append (out category_iter, root);
				//pipes_store.set (category_iter, 0, "Films", -1);

				//pipes_store.append (out product_iter, category_iter);
				//pipes_store.set (product_iter, 0, "Amores Perros", 1, "$7.99", -1);
				//pipes_store.append (out product_iter, category_iter);
				//pipes_store.set (product_iter, 0, "Twin Peaks", 1, "$14.99", -1);
				//pipes_store.append (out product_iter, category_iter);
				//pipes_store.set (product_iter, 0, "Vertigo", 1, "$20.49", -1);
			    }


            }
        }
}
