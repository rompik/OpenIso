		private void create_test_file () {

		    /* Test Block - DELETE AFTER CHECK */
            var _test_file = File.new_for_path (Environment.get_home_dir () + "/Dropbox/VALA/openiso/test/MTO.csv");
            var dos = new DataOutputStream (_test_file.create (FileCreateFlags.REPLACE_DESTINATION));
            //dos.put_string ("Total pipes number: " + this._ui_pipes.length.to_string() + "\n");

            for (int k = 0; k < _ui_pipes.length; k++) {
                var test_pipe = this._ui_pipes.index(k);
                //dos.put_string ("Pipe Name: " + test_pipe.Name + "\n");
                //dos.put_string ("   Pipe Spec: " + test_pipe.Spec + "\n");
                //dos.put_string ("   Pressure Reating: " + test_pipe.PressureRating.to_string() + "\n");
                //dos.put_string ("   Pipeline Type: " + test_pipe.LineType + "\n");
                //dos.put_string ("   Insulation Spec: " + test_pipe.Insulation + "\n");
                //dos.put_string ("   Tracing Spec: " + test_pipe.Tracing + "\n");
                //dos.put_string ("   Temperature: " + test_pipe.Temperature.to_string() + "\n");
                //dos.put_string ("   Pipe Members: \n");
                for (int j = 0; j < test_pipe.Components.length; j++){
                    var test_component = test_pipe.Components.index(j);
                    dos.put_string (test_component.Type + "\t" + test_component.Name + "\t" + test_component.Skey + "\n");

                }
            }

            //Test SVG file
            var _ui_sheet = new Core.Drawing.Sheet ();
            //var _ui_file_svg = new Core.Export.SVG ();
            var _ui_file_svg = new Core.Export.SVG (_ui_sheet);
		}
