package de.mrdocmoris.fitness;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Rect;
import android.util.Base64;

import com.getcapacitor.JSArray;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.google.mlkit.vision.common.InputImage;
import com.google.mlkit.vision.text.Text;
import com.google.mlkit.vision.text.TextRecognition;
import com.google.mlkit.vision.text.TextRecognizer;
import com.google.mlkit.vision.text.latin.TextRecognizerOptions;

/** Texterkennung mit Google ML Kit – läuft komplett auf dem Handy, ohne Internet. */
@CapacitorPlugin(name = "MlText")
public class MlTextPlugin extends Plugin {
    private TextRecognizer recognizer;

    @Override
    public void load() {
        recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS);
    }

    @PluginMethod
    public void recognize(PluginCall call) {
        String b64 = call.getString("image");
        if (b64 == null) { call.reject("Kein Bild"); return; }
        int comma = b64.indexOf(',');
        if (comma >= 0) b64 = b64.substring(comma + 1);
        final Bitmap bmp;
        try {
            byte[] bytes = Base64.decode(b64, Base64.DEFAULT);
            bmp = BitmapFactory.decodeByteArray(bytes, 0, bytes.length);
        } catch (Exception e) { call.reject("Bild ungültig: " + e.getMessage()); return; }
        if (bmp == null) { call.reject("Bild ungültig"); return; }
        InputImage image = InputImage.fromBitmap(bmp, 0);
        recognizer.process(image)
            .addOnSuccessListener(text -> {
                JSObject ret = new JSObject();
                JSArray lines = new JSArray();
                for (Text.TextBlock block : text.getTextBlocks()) {
                    for (Text.Line line : block.getLines()) {
                        JSObject o = new JSObject();
                        o.put("text", line.getText());
                        Rect r = line.getBoundingBox();
                        if (r != null) { o.put("x", r.left); o.put("y", r.top); o.put("w", r.width()); o.put("h", r.height()); }
                        lines.put(o);
                    }
                }
                ret.put("text", text.getText());
                ret.put("lines", lines);
                ret.put("width", bmp.getWidth());
                ret.put("height", bmp.getHeight());
                call.resolve(ret);
            })
            .addOnFailureListener(e -> call.reject("Texterkennung fehlgeschlagen: " + e.getMessage()));
    }
}
