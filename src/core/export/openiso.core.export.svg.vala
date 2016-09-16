/* openiso.core.export.svg.vala
 *
 * Copyright (C) 2016 Rompik <rompik@mail.ru>
 *
 * This file is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation; either version 3 of the
 * License, or (at your option) any later version.
 *
 * This file is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

using OpenIso;
using GLib;

namespace OpenIso.Core.Export {

    public class SVG : GLib.Object {

        //public SVG () {
        public SVG (Core.Drawing.Sheet _sheet) {
        //public SVG (File _file){

            File _svg_file = File.new_for_path (Environment.get_home_dir () + "/Dropbox/VALA/openiso/test/Drawing.svg");

            try {

                if( _svg_file.query_exists() == true){
                    //_svg_file.delete(null);
                }

                //FileOutputStream fos = _svg_file.create (FileCreateFlags.REPLACE_DESTINATION, null);
                //DataOutputStream dos = new DataOutputStream (fos);
                //dos.put_string ("""<svg height="297" width="420" xmlns:xlink="http://www.w3.org/1999/xlink">""" + "\n");
                //dos.put_string ("""<a xlink:href="http://www.w3schools.com/svg/" target="_blank">""" + "\n");
                //dos.put_string ("""<line x1="20" y1="5" x2="20" y2="292" style="stroke:rgb(255,0,0);stroke-width:1" />""" + "\n");
                //dos.put_string ("""<line x1="20" y1="5" x2="415" y2="5" style="stroke:rgb(255,0,0);stroke-width:1" />""" + "\n");
                //dos.put_string ("""<line x1="415" y1="5" x2="415" y2="292" style="stroke:rgb(255,0,0);stroke-width:1" />""" + "\n");
                //dos.put_string ("""<line x1="20" y1="292" x2="415" y2="292" style="stroke:rgb(255,0,0);stroke-width:1" />""" + "\n");
                //dos.put_string ("""<line x1="20" y1="20" x2="415" y2="292" style="stroke:rgb(255,0,0);stroke-width:1" />""" + "\n");
                //dos.put_string ("""</a>""" + "\n");
                //dos.put_string ("""</svg>""" + "\n");

            } catch (Error e) {

                 stderr.printf ("Error: %s\n", e.message);

            }
        }
    }
}
    
