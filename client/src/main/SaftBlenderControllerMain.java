package main;

import GUI.SaftBlenderGUI;

import javax.swing.SwingUtilities;

/**
 * Entry point, creates the GUI.
 * Created by Gustav "Tylhadras" Lundström on 2/27/15.
 */
public class SaftBlenderControllerMain {

    public static void main(final String [] args) {
        SwingUtilities.invokeLater(new Runnable() {
            @Override
            public void run() {
                if(args.length == 3) {
                    // Arg = 1 username, arg 2 = password, arg 3 = url.
                    SaftBlenderGUI gui = new SaftBlenderGUI(args[0], args[1], args[2]);
                    gui.buildAndShow();
                } else if(args.length == 2) {
                    // Arg 1 = username, arg 2 = password.
                    SaftBlenderGUI gui = new SaftBlenderGUI(args[0], args[1]);
                    gui.buildAndShow();
                } else if(args.length == 1) {
                    // Arg 1 = url.
                    SaftBlenderGUI gui = new SaftBlenderGUI(args[0]);
                    gui.buildAndShow();
                } else if(args.length == 0) {
                    // Use Default values.
                    SaftBlenderGUI gui = new SaftBlenderGUI();
                    gui.buildAndShow();
                } else {
                    // Catch-all-else, print help.
                    System.out.println("Usage: java -jar SaftBlenderGUI.jar url or username password url");
                }
            }
        });
    }
}
