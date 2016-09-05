using Gtk;

namespace OpenIso.UI{
        public class MainHeaderBar : Gtk.HeaderBar {

            public Gtk.Button btnLoad;
            public Gtk.Button btnSaveAs;
            public Gtk.Button btnSettings;
            public Gtk.Button btnHelp;

            public MainHeaderBar(){

                //Setup of Header Bar
                this.set_title(_("OpenIso"));
                this.set_subtitle(_("ver. 0.0.1 alpha"));
                this.set_show_close_button (true);

                btnLoad = new Gtk.Button.from_icon_name ("document-open", Gtk.IconSize.LARGE_TOOLBAR);
                btnLoad.set_tooltip_text (_("Import file"));
                this.pack_start (btnLoad);

                btnSaveAs = new Gtk.Button.from_icon_name ("document-save-as", Gtk.IconSize.LARGE_TOOLBAR);
                btnSaveAs.set_tooltip_text (_("Save As"));
                this.pack_start (btnSaveAs);

                btnHelp = new Gtk.Button.from_icon_name ("help-about", Gtk.IconSize.LARGE_TOOLBAR);
                btnHelp.set_tooltip_text (_("About"));
                this.pack_end (btnHelp);

                btnSettings = new Gtk.Button.from_icon_name ("preferences-system", Gtk.IconSize.LARGE_TOOLBAR);
                btnSettings.set_tooltip_text (_("Settings"));
                this.pack_end (btnSettings);

            }
        }
} 
