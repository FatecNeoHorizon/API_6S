package com.zeus.burndown.service;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Font;
import java.awt.Paint;
import java.awt.RenderingHints;
import java.awt.geom.Ellipse2D;
import java.awt.image.BufferedImage;
import java.io.File;
import java.text.SimpleDateFormat;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Date;
import java.util.List;

import javax.imageio.ImageIO;

import org.jfree.chart.ChartUtils;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.annotations.XYImageAnnotation;
import org.jfree.chart.axis.DateAxis;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.XYLineAndShapeRenderer;
import org.jfree.chart.title.TextTitle;
import org.jfree.chart.ui.RectangleInsets;
import org.jfree.data.time.Day;
import org.jfree.data.time.TimeSeries;
import org.jfree.data.time.TimeSeriesCollection;
import org.springframework.stereotype.Service;

import com.zeus.burndown.model.BurndownData;
@Service
public class BurndownChartGenerator {

    private static final int WIDTH = 1920;
    private static final int HEIGHT = 1080;
        private static final long HALF_DAY_IN_MILLIS = 12L * 60 * 60 * 1000;

    public void generateBurndownChart(BurndownData data,
                                      String outputPath,
                                      String logoPath) throws Exception {

        TimeSeries idealSeries = new TimeSeries("Ideal Line");
        TimeSeries realSeries = new TimeSeries("Real Line");

        List<LocalDate> dates = data.getDates();

        for (int i = 0; i <dates.size(); i++){

            LocalDate date = dates.get(i);

            Day day = new Day(date.getDayOfMonth(), date.getMonthValue(), date.getYear());

            idealSeries.add(day, data.getIdealLine().get(i));
            realSeries.add(day, data.getRealLine().get(i));
            
        }

        TimeSeriesCollection dataset = new TimeSeriesCollection();
        dataset.addSeries(idealSeries);
        dataset.addSeries(realSeries);

        DateAxis xAxis = new DateAxis("Sprint Days");
        NumberAxis yAxis = new NumberAxis("Remaining Hours");

        xAxis.setDateFormatOverride(new SimpleDateFormat("dd/MM"));
        configureXAxisRange(xAxis, dates);
        configureYAxisRange(yAxis, data);

        xAxis.setLabelFont(new Font("SansSerif", Font.BOLD, 20));
        xAxis.setTickLabelFont(new Font("SansSerif", Font.PLAIN, 16));

        yAxis.setLabelFont(new Font("SansSerif", Font.BOLD, 20));
        yAxis.setTickLabelFont(new Font("SansSerif", Font.PLAIN, 16));

        XYLineAndShapeRenderer renderer = new XYLineAndShapeRenderer(true, true) {

        @Override
        public Paint getItemPaint(int series, int item) {

                if (series == 1) { // série REAL

                Number real = dataset.getYValue(1, item);
                Number ideal = dataset.getYValue(0, item);

                if (real.doubleValue() > ideal.doubleValue()) {
                        return new Color(220, 53, 69); // vermelho (atrasado)
                } else {
                        return new Color(40, 167, 69); // verde (adiantado)
                }

                }

                return new Color(160,160,160); // linha ideal
        }
        };
        
        renderer.setSeriesPaint(0, new Color(150,150,150,120));

        renderer.setSeriesStroke(
                0,
                new BasicStroke(
                        3f,
                        BasicStroke.CAP_ROUND,
                        BasicStroke.JOIN_ROUND,
                        1f,
                        new float[]{10f,10f},
                        0f
                )
        );

        renderer.setSeriesShapesVisible(0, false);

        renderer.setSeriesPaint(1, new Color(33,150,243));

        renderer.setSeriesStroke(
                1,
                new BasicStroke(
                        4f,
                        BasicStroke.CAP_ROUND,
                        BasicStroke.JOIN_ROUND
                )
        );

        renderer.setSeriesShape(
                1,
                new Ellipse2D.Double(-4,-4,8,8)
        );

        renderer.setSeriesShapesVisible(1, true);

        XYPlot plot = new XYPlot(dataset, xAxis, yAxis, renderer);

        plot.setBackgroundPaint(new Color(250,250,250));

        plot.setDomainGridlinePaint(new Color(230,230,230));
        plot.setRangeGridlinePaint(new Color(230,230,230));

        plot.setDomainGridlineStroke(new BasicStroke(1f));
        plot.setRangeGridlineStroke(new BasicStroke(1f));

        plot.setAxisOffset(new RectangleInsets(20,20,20,20));

        plot.setOutlineVisible(false);


        plot.getDomainAxis().setAxisLineStroke(new BasicStroke(2f));
        plot.getRangeAxis().setAxisLineStroke(new BasicStroke(2f));

        JFreeChart chart = new JFreeChart(
                data.getSprintName(),
                new Font("SansSerif", Font.BOLD, 36),
                plot,
                true
        );

        chart.addSubtitle(new TextTitle(
                "Burndown Chart - Neo Horizon",
                new Font("SansSerif", Font.PLAIN, 24)
        ));

        chart.setBackgroundPaint(Color.WHITE);

        chart.getRenderingHints().put(
                RenderingHints.KEY_ANTIALIASING,
                RenderingHints.VALUE_ANTIALIAS_ON
        );

        if (logoPath != null) {
            BufferedImage logo = ImageIO.read(new File(logoPath));

            double maxX = plot.getDomainAxis().getRange().getUpperBound();
            double maxY = plot.getRangeAxis().getRange().getUpperBound();

            XYImageAnnotation annotation = new XYImageAnnotation(
                    maxX,
                    maxY,
                    logo,
                    org.jfree.chart.ui.RectangleAnchor.TOP_RIGHT
            );

            plot.addAnnotation(annotation);
        }

        ChartUtils.saveChartAsPNG(
                new File(outputPath),
                chart,
                WIDTH,
                HEIGHT
        );
        
    }

        private void configureXAxisRange(DateAxis xAxis, List<LocalDate> dates) {
                if (dates == null || dates.isEmpty()) {
                        return;
                }

                if (dates.size() == 1) {
                        long center = dates.get(0)
                                        .atStartOfDay(ZoneId.systemDefault())
                                        .toInstant()
                                        .toEpochMilli();

                        xAxis.setRange(new Date(center - HALF_DAY_IN_MILLIS), new Date(center + HALF_DAY_IN_MILLIS));
                        return;
                }

                long start = dates.get(0)
                                .atStartOfDay(ZoneId.systemDefault())
                                .toInstant()
                                .toEpochMilli();
                long end = dates.get(dates.size() - 1)
                                .atStartOfDay(ZoneId.systemDefault())
                                .toInstant()
                                .toEpochMilli();

                xAxis.setRange(new Date(start - HALF_DAY_IN_MILLIS), new Date(end + HALF_DAY_IN_MILLIS));
        }

        private void configureYAxisRange(NumberAxis yAxis, BurndownData data) {
                double max = 0d;

                if (data.getIdealLine() != null) {
                        for (Double value : data.getIdealLine()) {
                                if (value != null && value > max) {
                                        max = value;
                                }
                        }
                }

                if (data.getRealLine() != null) {
                        for (Double value : data.getRealLine()) {
                                if (value != null && value > max) {
                                        max = value;
                                }
                        }
                }

                double upperBound = max <= 0d ? 1d : Math.ceil(max * 1.1d);
                yAxis.setRange(0d, upperBound);
                yAxis.setStandardTickUnits(NumberAxis.createIntegerTickUnits());
        }

}
