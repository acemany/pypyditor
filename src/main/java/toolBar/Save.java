package individualClasses;

import java.awt.event.ActionEvent;
import java.io.FileWriter;
import java.io.IOException;

import javax.swing.AbstractAction;
import javax.swing.Action;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JTextArea;

public class Save extends JFrame{
	private JFileChooser fileSelect = new JFileChooser();
	private JTextArea textArea = new JTextArea(20, 60);
	
	 Action Save = new AbstractAction("Save File") {
	        @Override
	        public void actionPerformed(ActionEvent e) {
	            saveFile();
	        }
	    };
	    
	    public void saveFile() {
	        if (fileSelect.showSaveDialog(null) == JFileChooser.APPROVE_OPTION) {
	            FileWriter writer = null;
	            try {
	                writer = new FileWriter(fileSelect.getSelectedFile().getAbsolutePath() + ".txt");
	                textArea.write(writer);
	                writer.close();
	            } catch (IOException e) {
	                e.printStackTrace();
	            }
	        }
	    }
}
