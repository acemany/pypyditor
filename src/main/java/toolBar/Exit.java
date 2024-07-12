package individualClasses;

import java.awt.event.ActionEvent;

import javax.swing.AbstractAction;
import javax.swing.Action;
import javax.swing.JFrame;

public class Exit extends JFrame {

	 Action Exit = new AbstractAction("Exit") {
	        @Override
	        public void actionPerformed(ActionEvent e) {
	            System.exit(0);
	        }
	    };

}
