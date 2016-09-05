using Gtk;
using Gdk;
using GLib;
using Cairo;
using OpenIso;
using Constants;

namespace OpenIso.UI.Windows{
    public class Main : Gtk.ApplicationWindow {

        private Array <Core.Piping.Pipe> _ui_pipes = new Array <Core.Piping.Pipe> ();
        private Array <Core.Drawing.Sheet> _ui_sheets = new Array <Core.Drawing.Sheet> ();

        private Core.Import.IDF _ui_file_idf;

        public string SubTitle = "ver. 0.0.1";

        private string filename;


        // Create Pipe Explorer
        private TreeView PipesExplorer = new TreeView ();

        //Create Main Drawing Area
        private DrawingArea DrawingAreaMain = new DrawingArea ();
        //TODO: Delete variable
        private const int SIZE = 30;

        public Main (Gtk.Application application) {

            GLib.Object (application: application);
            this.set_default_size(600,400);
            this.window_position = Gtk.WindowPosition.CENTER;

            //Setup Header Bar with required buttons
            var HeaderBar = new Gtk.HeaderBar();
                HeaderBar.set_title("OpenIso");
                HeaderBar.set_subtitle(SubTitle);
                HeaderBar.set_show_close_button (true);

            var btnOpen = new Gtk.Button.from_icon_name ("document-open", Gtk.IconSize.LARGE_TOOLBAR);
                btnOpen.set_tooltip_text (_("Import file"));
                btnOpen.clicked.connect (() => { show_open_file_dialog(); });
                HeaderBar.pack_start (btnOpen);

            var btnSaveAs = new Gtk.Button.from_icon_name ("document-save-as", Gtk.IconSize.LARGE_TOOLBAR);
                btnSaveAs.set_tooltip_text (_("Save As"));
                btnSaveAs.clicked.connect (() => { show_save_file_dialog(); });
                HeaderBar.pack_start (btnSaveAs);

            var btnHelp = new Gtk.Button.from_icon_name ("help-about", Gtk.IconSize.LARGE_TOOLBAR);
                btnHelp.set_tooltip_text (_("About"));
                btnHelp.clicked.connect (() => { show_about_dialog(); });
                HeaderBar.pack_end (btnHelp);

            var btnSettings = new Gtk.Button.from_icon_name ("preferences-system", Gtk.IconSize.LARGE_TOOLBAR);
                btnSettings.set_tooltip_text (_("Settings"));
                HeaderBar.pack_end (btnSettings);

            //Scrolled Window for Pipe Explorer
            var ScrolledPipesExplorer = new ScrolledWindow (PipesExplorer.get_hadjustment (), PipesExplorer.get_vadjustment ());
                ScrolledPipesExplorer.set_shadow_type (ShadowType.ETCHED_IN);
                ScrolledPipesExplorer.add(PipesExplorer);
                ScrolledPipesExplorer.set_size_request (300, -1);

            //Setup Drawing Area
            var ScrolledDrawingArea = new ScrolledWindow ( null, null );
                ScrolledDrawingArea.set_shadow_type (ShadowType.ETCHED_IN);
                ScrolledDrawingArea.add(DrawingAreaMain);
                ScrolledDrawingArea.set_size_request (600, 600);

                DrawingAreaMain.draw.connect (on_draw);

            //Setup panel container
            var MainPanned = new Paned(Gtk.Orientation.HORIZONTAL);
                MainPanned.add1 (ScrolledPipesExplorer);
                MainPanned.add2 (ScrolledDrawingArea);

            //Setup application UI
            this.set_titlebar(HeaderBar);
            this.add(MainPanned);
            this.show_all();

        }

        // Method for open file
        private void show_open_file_dialog(){

            var file_chooser_import = new Gtk.FileChooserDialog (_("Import File"),
            this, Gtk.FileChooserAction.OPEN,
            _("Cancel"), Gtk.ResponseType.CANCEL,
            _("Open"),Gtk.ResponseType.ACCEPT);

            file_chooser_import.destroy_with_parent = true;
            file_chooser_import.set_current_folder (Environment.get_home_dir () + "/Dropbox/VALA/openiso/test");

            var filter = import_dialog_filter();

            file_chooser_import.add_filter(filter);

            var response = file_chooser_import.run();

            if (response == Gtk.ResponseType.ACCEPT) {

                var filename = File.new_for_path (file_chooser_import.get_filename());

                Core.Import.IDF _ui_file_idf = new Core.Import.IDF( filename );
                _ui_pipes = _ui_file_idf.Pipes;

                //var _ui_sheet = new Core.Drawing.Sheet();
                //var _ui_svg = new Core.Export.SVG( _ui_sheet );

            }

            file_chooser_import.dispose(); //no need for the dialog to be around anymore

            // Fill pipe explorer by founded pipes
            setup_pipes_explorer (PipesExplorer, _ui_pipes);

        }

        // Method for filtering idf files
        private static Gtk.FileFilter import_dialog_filter () {
            var file_filter = new Gtk.FileFilter ();
            file_filter.set_filter_name (_("IDF File"));
            file_filter.add_pattern ("*.idf");
            return file_filter;
        }

        // Method for saving file
        private void show_save_file_dialog(){
            var file_chooser_export = new Gtk.FileChooserDialog ("Save As", this, Gtk.FileChooserAction.SAVE,
                                                                 "_Cancel", Gtk.ResponseType.CANCEL,
                                                                 "_Save", Gtk.ResponseType.ACCEPT);

            var response = file_chooser_export.run();

            if (response == Gtk.ResponseType.ACCEPT) {
               filename = file_chooser_export.get_filename();

            //now do something with the filename
            }
            file_chooser_export.dispose(); //no need for the dialog to be around anymore
        }

        //Method for showing About form
        public void show_about_dialog() {
            var dialog = new AboutDialog();

	        dialog.set_modal (true);

            dialog.title = "About OpenIso";
            dialog.logo = new Pixbuf.from_file ("../../data/icons/openiso.png");
			dialog.authors = {"Roman Parygin"};
			dialog.documenters = null;
			dialog.translator_credits = _("translator-credits");


				    //dialog.program_name = "OpenIso";
            dialog.version = "0.0.1";
			dialog.comments = _("Utility for producing isometric by idf file.");
			dialog.copyright = _("Copyright © 2016 Roman Parygin");


			dialog.license_type = Gtk.License.GPL_3_0;
			dialog.wrap_license = false;

			dialog.website = "https://github.com/rompik/OpenIso";
			dialog.website_label = _("OpenIso Homepage");

            dialog.run();

	        dialog.response.connect ((response_id) => {
		        if ( response_id == Gtk.ResponseType.CANCEL
		            || response_id == Gtk.ResponseType.DELETE_EVENT
		            || response_id == Gtk.ResponseType.CLOSE ) {
			        dialog.destroy ();
		        }
	        });
        }

        //Method for filling Pipe Explorer
        private void setup_pipes_explorer (TreeView pipes_explorer, Array <Core.Piping.Pipe> pipes_array) {

            //TODO: Clean previous data for TreeView

            var pipes_store = new TreeStore (1, typeof (string));

            //pipes_explorer.clear();
		    pipes_explorer.enable_tree_lines = true;
		    pipes_explorer.set_model (pipes_store);
		    pipes_explorer.insert_column_with_attributes (-1, "Pipe Explorer", new CellRendererText (), "text", 0, null);

		    TreeIter root;
		    TreeIter category_iter;
		    TreeIter product_iter;

		    pipes_store.append (out root, null);
		    pipes_store.set (root, 0, "*", -1);
			for (int i = 0; i < pipes_array.length; i++) {

				pipes_store.append (out category_iter, root);
				pipes_store.set (category_iter, 0, pipes_array.index(i).Name, -1);
				for (int j = 0; j < pipes_array.index(i).Components.length; j++){
                  	pipes_store.append (out product_iter, category_iter);
                   	pipes_store.set (product_iter, 0, pipes_array.index(i).Components.index(j).Type, -1);

                }
			}
		    pipes_explorer.collapse_all ();

		}

		//Method for drawing
	    private bool on_draw (Widget da, Context ctx) {

	        //int width = get_allocated_width();
	        //int height = get_allocated_height();

            //var radius = double.min (width / 2, height /2 ) - 5;
            //ctx.arc (width, height, radius, 0, 2 * Math.PI);
            //ctx.set_source_rgb (1, 1, 1);
            //ctx.fill_preserve();

            //Setup color of outline
            //ctx.set_source_rgb (0, 0, 0);
            //ctx.stroke();

            //Setup thikness of line
            //ctx.set_line_width ( 1 );

            //Setup tolerance of line
            //ctx.set_tolerance ( 1 );

            //ctx.set_line_join (LineJoin.ROUND);
            //ctx.set_dash (new double[] {SIZE / 4.0, SIZE / 4.0}, 0);
            //stroke_shapes (ctx, 0, 0);

            //ctx.set_dash (null, 0);
            //stroke_shapes (ctx, 0, 3 * SIZE);

            //ctx.set_line_join (LineJoin.BEVEL);
            //stroke_shapes (ctx, 0, 6 * SIZE);

            //ctx.set_line_join (LineJoin.MITER);
            //stroke_shapes(ctx, 0, 9 * SIZE);

            //fill_shapes (ctx, 0, 12 * SIZE);

            //ctx.set_line_join (LineJoin.BEVEL);
            //fill_shapes (ctx, 0, 15 * SIZE);
            //ctx.set_source_rgb (1, 0, 0);
            //stroke_shapes (ctx, 0, 15 * SIZE);

            return true;
        }

        private delegate void DrawMethod ();

        public override void size_allocate (Allocation allocation) {
            //The base method will save the allocation and move/resize the
            // widget's GDK window if widget is already realised.
            base.size_allocate (allocation);
        }

    }
}

