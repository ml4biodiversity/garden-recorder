/*
 * @(#)CapturePlayback.java	1.11	99/12/03
 *
 * Copyright (c) 1999 Sun Microsystems, Inc. All Rights Reserved.
 *
 * Sun grants you ("Licensee") a non-exclusive, royalty free, license to use,
 * modify and redistribute this software in source and binary code form,
 * provided that i) this copyright notice and license appear on all copies of
 * the software; and ii) Licensee does not utilize the software in a manner
 * which is disparaging to Sun.
 *
 * This software is provided "AS IS," without a warranty of any kind. ALL
 * EXPRESS OR IMPLIED CONDITIONS, REPRESENTATIONS AND WARRANTIES, INCLUDING ANY
 * IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE OR
 * NON-INFRINGEMENT, ARE HEREBY EXCLUDED. SUN AND ITS LICENSORS SHALL NOT BE
 * LIABLE FOR ANY DAMAGES SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING
 * OR DISTRIBUTING THE SOFTWARE OR ITS DERIVATIVES. IN NO EVENT WILL SUN OR ITS
 * LICENSORS BE LIABLE FOR ANY LOST REVENUE, PROFIT OR DATA, OR FOR DIRECT,
 * INDIRECT, SPECIAL, CONSEQUENTIAL, INCIDENTAL OR PUNITIVE DAMAGES, HOWEVER
 * CAUSED AND REGARDLESS OF THE THEORY OF LIABILITY, ARISING OUT OF THE USE OF
 * OR INABILITY TO USE SOFTWARE, EVEN IF SUN HAS BEEN ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGES.
 *
 * This software is not designed or intended for use in on-line control of
 * aircraft, air traffic, aircraft navigation or aircraft communications; or in
 * the design, construction, operation or maintenance of any nuclear
 * facility. Licensee represents and warrants that it will not use or
 * redistribute the Software for such purposes.
 */


import javax.sound.sampled.*;
import javax.swing.*;
import javax.swing.border.BevelBorder;
import javax.swing.border.CompoundBorder;
import javax.swing.border.EmptyBorder;
import javax.swing.border.SoftBevelBorder;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.font.FontRenderContext;
import java.awt.font.LineBreakMeasurer;
import java.awt.font.TextAttribute;
import java.awt.font.TextLayout;
import java.awt.geom.Line2D;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.text.AttributedCharacterIterator;
import java.text.AttributedString;
import java.util.Enumeration;
import java.util.Vector;


/**
 *  Capture/Playback sample.  Record audio in different formats
 *  and then playback the recorded audio.  The captured audio can 
 *  be saved either as a WAVE, AU or AIFF.  Or load an audio file
 *  for streaming playback.
 *
 * @version @(#)CapturePlayback.java	1.11	99/12/03
 * @author Brian Lichtenwalter  
 */


public class RecordingTool extends JPanel implements ActionListener, ControlContext {

    final int bufSize = 16384;

    FormatControls formatControls = new FormatControls();
    Capture capture = new Capture();
    //Playback playback = new Playback();

    AudioInputStream audioInputStream;

    JButton playB, captB, pausB, loadB;
    JButton auB, aiffB, waveB;
    JTextField textField;
    JProgressBar progressBar_th0, progressBar_th1, progressBar_th2, progressBar_th3;
    String fileName = "untitled";
    String errStr;
    double duration, seconds;
    File file;
    Vector lines = new Vector();

    FirstInFirstOut fifo  = new FirstInFirstOut();
    public RecordingTool() {
        setLayout(new BorderLayout());
        EmptyBorder eb = new EmptyBorder(5,5,5,5);
        SoftBevelBorder sbb = new SoftBevelBorder(SoftBevelBorder.LOWERED);
        setBorder(new EmptyBorder(5,5,5,5));

        JPanel p1 = new JPanel();
        p1.setLayout(new BoxLayout(p1, BoxLayout.X_AXIS));
        p1.add(formatControls);

        JPanel p2 = new JPanel();
        p2.setBorder(sbb);
        p2.setLayout(new BoxLayout(p2, BoxLayout.Y_AXIS));

        JPanel buttonsPanel = new JPanel();
        buttonsPanel.setBorder(new EmptyBorder(10,0,5,0));
        playB = addButton("Play", buttonsPanel, false);
        captB = addButton("Record", buttonsPanel, true);
        pausB = addButton("Pause", buttonsPanel, false);
        loadB = addButton("Load...", buttonsPanel, true);
        p2.add(buttonsPanel);

        JPanel samplingPanel = new JPanel(new BorderLayout());
        eb = new EmptyBorder(10,20,20,20);
        samplingPanel.setBorder(new CompoundBorder(eb, sbb));
        p2.add(samplingPanel);

        JPanel savePanel = new JPanel();
        savePanel.setLayout(new BoxLayout(savePanel, BoxLayout.Y_AXIS));
     
        JPanel saveTFpanel = new JPanel();
        saveTFpanel.add(new JLabel("Folder to store:  "));
        saveTFpanel.add(textField = new JTextField(fileName));
        textField.setPreferredSize(new Dimension(140,25));
        savePanel.add(saveTFpanel);

        p2.add(savePanel);

        p1.add(p2);
        add(p1);
    }


    public void open() { }


    public void close() {

        if (capture.thread != null) {
            captB.doClick(0);
        }

    }


    private JButton addButton(String name, JPanel p, boolean state) {
        JButton b = new JButton(name);
        b.addActionListener(this);
        b.setEnabled(state);
        p.add(b);
        return b;
    }

    public static void showInfoDialog() {
        final String msg =
                "When running the Java Sound demo as an applet these permissions\n" +
                        "are necessary in order to load/save files and record audio :  \n\n"+
                        "grant { \n" +
                        "  permission java.io.FilePermission \"<<ALL FILES>>\", \"read, write\";\n" +
                        "  permission javax.sound.sampled.AudioPermission \"record\"; \n" +
                        "  permission java.util.PropertyPermission \"user.dir\", \"read\";\n"+
                        "}; \n\n" +
                        "The permissions need to be added to the .java.policy file.";
        new Thread(new Runnable() {
            public void run() {
                JOptionPane.showMessageDialog(null, msg, "Applet Info", JOptionPane.INFORMATION_MESSAGE);
            }
        }).start();
    }

    public void actionPerformed(ActionEvent e) {
        Object obj = e.getSource();
        String folderName = "test";
        if (obj.equals(captB)) {
            if (captB.getText().startsWith("Record")) {
                file = null;
                try {
                    folderName = textField.getText().trim();
                    capture.start(folderName);
                } catch (IOException ex) {
                    throw new RuntimeException(ex);
                }
                fileName = "untitled";
                loadB.setEnabled(false);
                playB.setEnabled(false);
                pausB.setEnabled(true);
                captB.setText("Stop");
            } else {
                lines.removeAllElements();  
                capture.stop();
                loadB.setEnabled(true);
                playB.setEnabled(true);
                pausB.setEnabled(false);
                captB.setText("Record");
            }
        } else if (obj.equals(pausB)) {
            if (pausB.getText().startsWith("Pause")) {
                if (capture.thread != null) {
                    capture.line.stop();
                }
                pausB.setText("Resume");
            } else {
                if (capture.thread != null) {
                    capture.line.start();
                }
                pausB.setText("Pause");
            }
        } else if (obj.equals(loadB)) {
            try {
                File file = new File(System.getProperty("user.dir"));
                JFileChooser fc = new JFileChooser(file);
                fc.setFileFilter(new javax.swing.filechooser.FileFilter () {
                    public boolean accept(File f) {
                        if (f.isDirectory()) {
                            return true;
                        }
                        String name = f.getName();

                        return false;
                    }
                    public String getDescription() {
                        return ".au, .wav, .aif";
                    }
                });

                if (fc.showOpenDialog(null) == JFileChooser.APPROVE_OPTION) {
                }
            } catch (SecurityException ex) { 
                showInfoDialog();
                ex.printStackTrace();
            } catch (Exception ex) { 
                ex.printStackTrace();
            }
        }
    }

    /** 
     * Reads data from the input channel and writes to the output stream
     */
    class Capture implements Runnable {
        TargetDataLine line;
        Thread thread;

        //FirstInFirstOut fifo  = new FirstInFirstOut();
        public void start(String folderName) throws IOException {
            errStr = null;
            thread = new Thread(this);
            thread.setName("Capture");
            thread.start();
            fifo.initialize(folderName);
        }

        public void stop()  {
            thread = null;
            try {
                fifo.close();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
        
        private void shutDown(String message) {
            if ((errStr = message) != null && thread != null) {
                thread = null;
                loadB.setEnabled(true);
                playB.setEnabled(true);
                pausB.setEnabled(false);
                //auB.setEnabled(true);
                //aiffB.setEnabled(true);
                //waveB.setEnabled(true);
                captB.setText("Record");
                System.err.println(errStr);
                try {
                    fifo.close();
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            }
        }

        public void run() {
            duration = 0;
            audioInputStream = null;
            
            // define the required attributes for our line, 
            // and make sure a compatible line is supported.

            AudioFormat format = formatControls.getFormat();
            DataLine.Info info = new DataLine.Info(TargetDataLine.class, 
                format);
                        
            if (!AudioSystem.isLineSupported(info)) {
                shutDown("Line matching " + info + " not supported.");
                return;
            }

            // get and open the target data line for capture.

            try {
                line = (TargetDataLine) AudioSystem.getLine(info);
                line.open(format, line.getBufferSize());
            } catch (LineUnavailableException ex) { 
                shutDown("Unable to open the line: " + ex);
                return;
            } catch (SecurityException ex) { 
                shutDown(ex.toString());
                showInfoDialog();
                return;
            } catch (Exception ex) { 
                shutDown(ex.toString());
                return;
            }

            // play back the captured audio data
            int frameSizeInBytes = format.getFrameSize();
            int inputChannels = format.getChannels();
            int bufferLengthInFrames = line.getBufferSize() / 8;
            int bufferLengthInBytes = bufferLengthInFrames * frameSizeInBytes;
            byte[] data = new byte[bufferLengthInBytes];
            int numBytesRead;
            
            line.start();

            while (thread != null) {
                if((numBytesRead = line.read(data, 0, bufferLengthInBytes)) == -1) {
                    break;
                }
                fifo.write_bytes_to_buffer(data, inputChannels);
                progressBar_th0.setValue((int)(fifo.NF.min_variance));
                progressBar_th1.setValue((int)(fifo.hellMeasures[0]*100));
                progressBar_th2.setValue((int)(fifo.hellMeasures[1]*100));
                progressBar_th3.setValue((int)(fifo.hellMeasures[2]*100));
            }

            // we reached the end of the stream.  stop and close the line.
            line.stop();
            line.close();
            line = null;

            // load bytes into the audio input stream for playback

            long milliseconds = (long)((11025 * 1000) / format.getFrameRate());
            duration = milliseconds / 1000.0;
        }
    } // End class Capture
 

    /**
     * Controls for the AudioFormat.
     */
    class FormatControls extends JPanel {
    
        Vector groups = new Vector();
        JToggleButton mono, stereo, rate441, rate48, rate196;
    
        public FormatControls() {
            setLayout(new GridLayout(0,1));
            EmptyBorder eb = new EmptyBorder(0,0,0,5);
            BevelBorder bb = new BevelBorder(BevelBorder.LOWERED);
            CompoundBorder cb = new CompoundBorder(eb, bb);
            setBorder(new CompoundBorder(cb, new EmptyBorder(8,5,5,5)));

            JPanel p1 = new JPanel();
            ButtonGroup sampleRateGroup = new ButtonGroup();
            rate441 = addToggleButton(p1, sampleRateGroup, "44100", false);
            rate48 = addToggleButton(p1, sampleRateGroup, "48000", true);
            rate196 = addToggleButton(p1, sampleRateGroup, "19600", false);
            add(p1);

            groups.addElement(sampleRateGroup);
    
            JPanel p2 = new JPanel();
            ButtonGroup channelsGroup = new ButtonGroup();
            mono = addToggleButton(p2, channelsGroup, "mono", false);
            stereo = addToggleButton(p2, channelsGroup, "stereo", true);
            add(p2);
            groups.addElement(channelsGroup);

            JPanel p3 = new JPanel();
            p3.setLayout(new GridLayout(4, 3));
            JSlider th0_slider = new JSlider(0,100,20);
            JLabel status_th0 = new JLabel("Variance gate  : 20", JLabel.LEFT);

            JSlider th1_slider = new JSlider(0,100,50);
            JLabel status_th1 = new JLabel("Temporal flatness  : 0.5", JLabel.LEFT);
            JSlider th2_slider = new JSlider(0,100,50);
            JLabel status_th2 = new JLabel("Spectrum max score : 0.5", JLabel.LEFT);
            JSlider th3_slider = new JSlider(0,100,50);
            JLabel status_th3 = new JLabel("Spectrum divergence: 0.5", JLabel.LEFT);
            progressBar_th0 = new JProgressBar(0, 100);
            progressBar_th0.setValue(0);
            progressBar_th1 = new JProgressBar(0, 100);
            progressBar_th1.setValue(10);
            progressBar_th2 = new JProgressBar(0, 100);
            progressBar_th2.setValue(20);
            progressBar_th3 = new JProgressBar(0, 100);
            progressBar_th3.setValue(30);
            p3.add(th0_slider); p3.add(status_th0); p3.add(progressBar_th0);
            p3.add(th1_slider); p3.add(status_th1); p3.add(progressBar_th1);
            p3.add(th2_slider); p3.add(status_th2); p3.add(progressBar_th2);
            p3.add(th3_slider); p3.add(status_th3); p3.add(progressBar_th3);
            // Add change listener to the slider
            th0_slider.addChangeListener(new ChangeListener() {
                public void stateChanged(ChangeEvent e) {
                    fifo.varianceGate = ((double)((JSlider)e.getSource()).getValue());
                    status_th0.setText("Variance gate value  : " + fifo.varianceGate);
                }
            });            th1_slider.addChangeListener(new ChangeListener() {
                public void stateChanged(ChangeEvent e) {
                    fifo.hellTh1 = ((double)((JSlider)e.getSource()).getValue())/100.0;
                    status_th1.setText("Temporal flatness  : " + fifo.hellTh1);
                }
            });
            th2_slider.addChangeListener(new ChangeListener() {
                public void stateChanged(ChangeEvent e) {
                    fifo.hellTh2 = ((double)((JSlider)e.getSource()).getValue())/100.0;
                    status_th2.setText("Spectrum max score: " + fifo.hellTh2);
                }
            });
            th3_slider.addChangeListener(new ChangeListener() {
                public void stateChanged(ChangeEvent e) {
                    fifo.hellTh3 = ((double)((JSlider)e.getSource()).getValue())/100.0;
                    status_th3.setText("Spectrum max score : " + fifo.hellTh3);
                }
            });
            add(p3);
        }
    
        private JToggleButton addToggleButton(JPanel p, ButtonGroup g, 
                                     String name, boolean state) {
            JToggleButton b = new JToggleButton(name, state);
            p.add(b);
            g.add(b);
            return b;
        }

        public AudioFormat getFormat() {

            Vector v = new Vector(groups.size());
            for (int i = 0; i < groups.size(); i++) {
                ButtonGroup g = (ButtonGroup) groups.get(i);
                for (Enumeration e = g.getElements();e.hasMoreElements();) {
                    AbstractButton b = (AbstractButton) e.nextElement();
                    if (b.isSelected()) {
                        v.add(b.getText());
                        break;
                    }
                }
            }

            AudioFormat.Encoding encoding = AudioFormat.Encoding.PCM_SIGNED;
            float rate = Float.valueOf((String) v.get(0)).floatValue();
            int sampleSize = 16;
            int channels = ((String) v.get(1)).equals("mono") ? 1 : 2;

            return new AudioFormat(encoding, rate, sampleSize,
                          channels, (sampleSize/8)*channels, rate, true);
        }
    } // End class FormatControls




    public static void main(String s[]) {
        RecordingTool capturePlayback = new RecordingTool();
        capturePlayback.open();
        JFrame f = new JFrame("Capture/Playback");
        f.addWindowListener(new WindowAdapter() {
            public void windowClosing(WindowEvent e) { System.exit(0); }
        });
        f.getContentPane().add("Center", capturePlayback);
        f.pack();
        Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
        int w = 920;
        int h = 340;
        f.setLocation(screenSize.width/2 - w/2, screenSize.height/2 - h/2);
        f.setSize(w, h);
        f.show();
    }
} 
