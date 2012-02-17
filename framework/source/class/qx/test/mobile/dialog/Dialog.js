/* ************************************************************************

   qooxdoo - the new era of web development

   http://qooxdoo.org

   Copyright:
     2011 1&1 Internet AG, Germany, http://www.1und1.de

   License:
     LGPL: http://www.gnu.org/licenses/lgpl.html
     EPL: http://www.eclipse.org/org/documents/epl-v10.php
     See the LICENSE file in the project's top-level directory for details.

   Authors:
     * Tino Butz (tbtz)

************************************************************************ */

qx.Class.define("qx.test.mobile.dialog.Dialog",
{
  extend : qx.test.mobile.MobileTestCase,

  members :
  {
    testShowHide : function()
    {
      var dialog = new qx.ui.mobile.dialog.Dialog();
      
     this.assertFalse(dialog.__getBlocker().isShown(), 'After usage of getBlocker, a blocker instance should be shown.');
     
     // Modal mode false test cases, no changes expected.
     dialog.setModal(false);
     dialog.show();
     
     dialog.hide();
     this.assertFalse(dialog.__getBlocker().isShown(), 'Modal mode is false, called dialog.hide(), blocker should be still hidden.');
     
     dialog.show();
     this.assertFalse(dialog.__getBlocker().isShown(), 'Modal mode is false, called dialog.show(), blocker should be still hidden.');
      
     // Modal mode true test cases
     dialog.setModal(true);
     
     dialog.show();
     this.assertTrue(dialog.__getBlocker().isShown(), 'Modal mode is true, called dialog.show(), Blocker should be shown.');
     
     dialog.hide();
     this.assertFalse(dialog.__getBlocker().isShown(), 'Modal mode is true, called dialog.hide(), Blocker should not be shown.');
    }
  }

});
