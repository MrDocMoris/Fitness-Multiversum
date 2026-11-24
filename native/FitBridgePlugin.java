package de.mrdocmoris.fitness;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.speech.RecognizerIntent;

import androidx.activity.result.ActivityResult;

import com.getcapacitor.JSArray;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.ActivityCallback;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.util.ArrayList;

/** Brücke für das Startbildschirm-Widget und die Spracheingabe. */
@CapacitorPlugin(name = "FitBridge")
public class FitBridgePlugin extends Plugin {
    private SharedPreferences prefs() { return getContext().getSharedPreferences("fitm", Context.MODE_PRIVATE); }

    @PluginMethod
    public void setWidget(PluginCall call) {
        SharedPreferences.Editor e = prefs().edit();
        for (String k : new String[]{"date", "value", "label", "sub", "water", "goal", "wgoal"}) e.putString("w_" + k, call.getString(k, ""));
        e.apply();
        FitWidget.updateAll(getContext());
        call.resolve();
    }

    @PluginMethod
    public void listen(PluginCall call) {
        Intent i = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        i.putExtra(RecognizerIntent.EXTRA_LANGUAGE, call.getString("lang", "de-DE"));
        i.putExtra(RecognizerIntent.EXTRA_PROMPT, call.getString("prompt", "Was hast du gegessen?"));
        i.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3);
        try { startActivityForResult(call, i, "speechResult"); }
        catch (Exception e) { call.reject("Spracherkennung nicht verfügbar"); }
    }

    @ActivityCallback
    private void speechResult(PluginCall call, ActivityResult result) {
        if (call == null) return;
        JSObject r = new JSObject();
        ArrayList<String> m = (result.getResultCode() == Activity.RESULT_OK && result.getData() != null) ? result.getData().getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS) : null;
        r.put("text", m != null && !m.isEmpty() ? m.get(0) : "");
        JSArray a = new JSArray(); if (m != null) for (String s : m) a.put(s);
        r.put("all", a);
        call.resolve(r);
    }
}
