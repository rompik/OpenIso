using GLib;

namespace OpenIso.Drawing.Shape {
                public class Rectangle : Object {

                    private float rectWidth = 1.0f;
                    private float rectHeight = 1.0f;
                    //Position of centre of rectangle (align: Centre and Middle)
                    private float[] rectPosition = {0, 0};
                    private string rectAlignHorizontal = _("Left");
                    private string rectAlignVertical = _("Bottom");
                    private string rectLineType = _("Simple");
                    private float rectLineThick = 1.0f;

                    /* Constructor */
                    public Rectangle (float _rectWidth, float _rectHeight, float[] _rectPosition) {

                    }

                    /*
                     * = Properties =
                     */

                   public float Width {
                        get { return rectWidth; }
                        set { rectWidth = value; }
                   }

                   public float Height {
                        get { return rectHeight; }
                        set { rectHeight = value; }
                   }

                   public float[] Position{
                        get { return rectPosition; }
                        set { rectPosition = value; }
                   }

                   public string AlignHorizontal{
                        get { return rectAlignHorizontal; }
                        set { rectAlignHorizontal = value; }
                   }

                   public string AlignVertical{
                        get { return rectAlignVertical; }
                        set { rectAlignVertical = value; }
                   }

                   public string LineType {
                        get { return rectLineType; }
                        set { rectLineType = value; }
                   }

                   public float LineThickness {
                        get { return rectLineThick; }
                        set { rectLineThick = value; }
                   }

                   /*private float[2] CalculateNewPosition(string _newAlign) {
                       var _posX = rectPosition[1]
                       var _posY = rectPosition[2]

                       switch(_newAlign){
                            case "top":
                                _posX = rectPosition[1]
                                _posY = rectPosition[2] - rectHeight / 2

                            case "middle":
                                _posX = rectPosition[1]
                                _posY = rectPosition[2] - rectHeight / 2

                            case "bottom":

                            case "left":

                            case "centre":

                            case "right":
                        default:
                            return

                        }

                   }
                   *
                   */

                }
            }
