using Gtk;
using Cairo;

namespace OpenIso.UI {
    public class Drawing : Gtk.DrawingArea {

        private Time time;
        private int minute_offset;
        private bool dragging;

        public signal void time_changed (int hour, int minute);

        public Drawing () {

            add_events ( Gdk.EventMask.BUTTON_PRESS_MASK
                       | Gdk.EventMask.BUTTON_RELEASE_MASK
                       | Gdk.EventMask.POINTER_MOTION_MASK );

            update();

            //This update clock once a second

            Timeout.add (1000, update);

        }

        public override bool draw (Cairo.Context cr) {
            var x = get_allocated_width () / 2;
            var y = get_allocated_height () / 2;
            var radius = double.min ( x, y - 5);

            //clock back
            cr.arc ( x, y, radius, 0, 2 * Math.PI );
            cr.set_source_rgb (1, 1, 1);
            cr.fill_preserve ();
            cr.set_source_rgb (0, 0, 0);
            cr.stroke ();

            //clock strike

            for ( int i = 0; i < 12; i++ ) {
                int inset;
                cr.save (); //stack pen-size

                if ( i % 3 == 0) {
                    inset = (int) (0.2 * radius);

                } else {
                    inset = (int) (0.1 * radius);
                    cr.set_line_width (0.5 * cr.get_line_width());

                }

                cr.move_to (x + (radius - inset) * Math.cos (i * Math.PI / 6),
                            y + (radius - inset) * Math.sin (i * Math.PI / 6));

                cr.line_to (x + radius * Math.cos (i * Math.PI / 6),
                            y + radius * Math.sin (i * Math.PI / 6));

                cr.stroke();
                cr.restore(); //stack pen-size

            }

            //clock hands

            var hours = this.time.hour;
            var minutes = this.time.minute + this.minute_offset;
            var seconds = this.time.second;

            // hour hand

            cr.save ();
            cr.set_line_width ( 2.5 * cr.get_line_width ());
            cr.move_to (x, y);
            cr.line_to (x + radius / 2 * Math.sin ( Math.PI / 6 * hours + Math.PI / 360 * minutes),
                        y + radius / 2 * -Math.cos ( Math.PI / 6 * hours + Math.PI / 360 * minutes));

            cr.stroke ();
            cr.restore ();

            //minute hand
            cr.move_to (x,y);
            cr.line_to (x + radius * 0.75 * Math.sin ( Math.PI / 30 * minutes),
                        y + radius * 0.75 * -Math.cos (Math.PI / 30 * minutes));
            cr.stroke();

            //second hand
            // operates identically to the minute hand
            cr.save ();
            cr.set_source_rgb (1, 0, 0); //red
            cr.move_to (x, y);
            cr.line_to (x + radius * 0.7 * Math.sin ( Math.PI / 30 * seconds),
                        y + radius * 0.7 * -Math.cos (Math.PI / 30 * seconds));
            cr.stroke ();
            cr.restore ();

            return false;

        }

        public override bool button_press_event ( Gdk.EventButton event ) {
            var minutes = this.time.minute + this.minute_offset;

            var px = event.x - get_allocated_width () / 2;
            var py = get_allocated_height () /2 - event.y;
            var lx = Math.sin ( Math.PI / 30 * minutes );
            var ly = Math.cos ( Math.PI / 30 * minutes );
            var u = lx * px + ly * py;

            if (u < 0) {
                return false;
            }

            var d2 = Math.pow (px - u * lx, 2) + Math.pow (py - u * ly, 2);
            if (d2 < 25) {
                this.dragging = true;
                print ("got minute hand\n");
            }

            return false;
        }

        public override bool button_release_event (Gdk.EventButton event) {
            if (this.dragging) {
                emit_time_changed_signal ((int) event.x, (int) event.y);
            }

            return false;
        }

        private void emit_time_changed_signal (int x, int y) {
            x -= get_allocated_width () / 2;
            y -= get_allocated_height () / 2;

            var phi = Math.atan2 (x, -y);
            if (phi < 0) {
                phi += Math.PI * 2;
            }

            var hour = this.time.hour;
            var minute = (int) (phi * 30 / Math.PI);
            this.minute_offset = minute - this.time.minute;
            redraw_canvas ();

            time_changed (hour, minute);
        }

        private bool update () {
            this.time = Time.local (time_t ());
            redraw_canvas ();
            return true;
        }

        private void redraw_canvas () {
            var window = get_window ();
            if (null == window) {
                return;
            }

            var region = window.get_clip_region ();
            window.invalidate_region (region, true);
            window.process_updates (true);
        }
    }
}

