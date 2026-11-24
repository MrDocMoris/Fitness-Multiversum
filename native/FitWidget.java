package de.mrdocmoris.fitness;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.widget.RemoteViews;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/** Startbildschirm-Widget: kcal übrig, Gegessen/Ziel, Wasser. Daten schreibt die App (FitBridge.setWidget). */
public class FitWidget extends AppWidgetProvider {
    @Override
    public void onUpdate(Context ctx, AppWidgetManager m, int[] ids) {
        for (int id : ids) m.updateAppWidget(id, views(ctx));
    }

    private static PendingIntent link(Context ctx, String url, int code) {
        Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse(url), ctx, MainActivity.class);
        i.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        return PendingIntent.getActivity(ctx, code, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    static RemoteViews views(Context ctx) {
        SharedPreferences sp = ctx.getSharedPreferences("fitm", Context.MODE_PRIVATE);
        String today = new SimpleDateFormat("yyyy-MM-dd", Locale.GERMANY).format(new Date());
        boolean fresh = today.equals(sp.getString("w_date", ""));
        boolean any = !sp.getString("w_goal", "").isEmpty();
        RemoteViews v = new RemoteViews(ctx.getPackageName(), R.layout.fit_widget);
        v.setTextViewText(R.id.w_value, fresh ? sp.getString("w_value", "–") : (any ? sp.getString("w_goal", "–") : "–"));
        v.setTextViewText(R.id.w_label, fresh ? sp.getString("w_label", "kcal übrig") : "kcal übrig");
        v.setTextViewText(R.id.w_sub, fresh ? sp.getString("w_sub", "") : (any ? "Neuer Tag – noch nichts eingetragen" : "App öffnen, um zu starten"));
        v.setTextViewText(R.id.w_water, fresh ? sp.getString("w_water", "") : (any ? "💧 0 / " + sp.getString("w_wgoal", "2") + " l" : ""));
        v.setOnClickPendingIntent(R.id.w_root, link(ctx, "fitm://home", 81));
        v.setOnClickPendingIntent(R.id.w_add, link(ctx, "fitm://add", 82));
        v.setOnClickPendingIntent(R.id.w_drink, link(ctx, "fitm://water", 83));
        return v;
    }

    public static void updateAll(Context ctx) {
        try {
            AppWidgetManager m = AppWidgetManager.getInstance(ctx);
            int[] ids = m.getAppWidgetIds(new ComponentName(ctx, FitWidget.class));
            for (int id : ids) m.updateAppWidget(id, views(ctx));
        } catch (Exception e) { /* kein Widget */ }
    }
}
