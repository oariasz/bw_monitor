Make Mac OS exe file


1. Make sure you have a main.py (or equivalent entry point) that acts as the starting point of your application

2. Install PyInstaller
   Open your terminal and install PyInstaller. Go to the project directory and execute the command:

   pip install pyinstaller

3. Generate the Executable
   Run the following command:

   pyinstaller --onefile --windowed main.py

   YOU ARE DONE!!! ------------------------------------

4. Explanation of the Flags:

   --onefile: Combines all dependencies into a single executable file.
   --windowed (optional): Suppresses the terminal window when running GUI-based applications.

5. Locate the Executable
   After running the above commmand:

   - PyInstaller creates a dist directory in your project directory
   - Inside dist, you'll find the generated executable file (e.g. main).


6. Code-Signing the Application (Optional)
   For Mac OS security compliancer, you may need to code-sign your application:

   codesign --deep --force --sign "Your Developer ID" /path/to/your/executable¡