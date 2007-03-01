/* ************************************************************************

   qooxdoo - the new era of web development

   http://qooxdoo.org

   Copyright:
     2006 STZ-IDA, Germany, http://www.stz-ida.de

   License:
     LGPL: http://www.gnu.org/licenses/lgpl.html
     EPL: http://www.eclipse.org/org/documents/epl-v10.php
     See the LICENSE file in the project's top-level directory for details.

   Authors:
     * Til Schneider (til132)

************************************************************************ */

/* ************************************************************************

#module(ui_table)

************************************************************************ */

/**
 * The default data cell renderer.
 */
qx.Class.define("qx.ui.table.DefaultDataCellRenderer",
{
  extend : qx.ui.table.AbstractDataCellRenderer,




  /*
  *****************************************************************************
     CONSTRUCTOR
  *****************************************************************************
  */

  construct : function() {
    this.base(arguments);
  },




  /*
  *****************************************************************************
     STATICS
  *****************************************************************************
  */

  statics :
  {
    STYLEFLAG_ALIGN_RIGHT : 1,
    STYLEFLAG_BOLD        : 2,
    STYLEFLAG_ITALIC      : 4
  },




  /*
  *****************************************************************************
     PROPERTIES
  *****************************************************************************
  */

  properties :
  {
    /**
     * Whether the alignment should automatically be set according to the cell value.
     * If true numbers will be right-aligned.
     */
    useAutoAlign :
    {
      _legacy      : true,
      type         : "boolean",
      defaultValue : true,
      allowNull    : false
    }
  },




  /*
  *****************************************************************************
     MEMBERS
  *****************************************************************************
  */

  members :
  {
    // overridden
    /**
     * TODOC
     *
     * @type member
     * @param cellInfo {var} TODOC
     * @return {var} TODOC
     */
    _getCellStyle : function(cellInfo)
    {
      var style = qx.ui.table.AbstractDataCellRenderer.prototype._getCellStyle(cellInfo);

      var stylesToApply = this._getStyleFlags(cellInfo);

      if (stylesToApply & qx.ui.table.DefaultDataCellRenderer.STYLEFLAG_ALIGN_RIGHT) {
        style += ";text-align:right";
      }

      if (stylesToApply & qx.ui.table.DefaultDataCellRenderer.STYLEFLAG_BOLD) {
        style += ";font-weight:bold";
      }

      if (stylesToApply & qx.ui.table.DefaultDataCellRenderer.STYLEFLAG_ITALIC) {
        style += ";font-style:italic";
      }

      return style;
    },


    /**
     * Determines the styles to apply to the cell
     *
     * @type member
     * @param cellInfo {Object} cellInfo of the cell
     * @return {var} the sum of any of the STYLEFLAGS defined below
     */
    _getStyleFlags : function(cellInfo)
    {
      if (this.getUseAutoAlign())
      {
        if (typeof cellInfo.value == "number") {
          return qx.ui.table.DefaultDataCellRenderer.STYLEFLAG_ALIGN_RIGHT;
        }
      }
    },

    // overridden
    /**
     * TODOC
     *
     * @type member
     * @param cellInfo {var} TODOC
     * @return {var} TODOC
     */
    _getContentHtml : function(cellInfo) {
      return qx.html.String.escape(this._formatValue(cellInfo));
    },

    // overridden
    /**
     * TODOC
     *
     * @type member
     * @param cellInfo {var} TODOC
     * @param cellElement {var} TODOC
     * @return {void}
     */
    updateDataCellElement : function(cellInfo, cellElement)
    {
      var clazz = qx.ui.table.DefaultDataCellRenderer;
      var style = cellElement.style;

      var stylesToApply = this._getStyleFlags(cellInfo);

      if (stylesToApply & clazz.STYLEFLAG_ALIGN_RIGHT) {
        style.textAlign = "right";
      } else {
        style.textAlign = "";
      }

      if (stylesToApply & clazz.STYLEFLAG_BOLD) {
        style.fontWeight = "bold";
      } else {
        style.fontWeight = "";
      }

      if (stylesToApply & clazz.STYLEFLAG_ITALIC) {
        style.fontStyle = "ital";
      } else {
        style.fontStyle = "";
      }

      var textNode = cellElement.firstChild;

      if (textNode != null) {
        textNode.nodeValue = this._formatValue(cellInfo);
      } else {
        cellElement.innerHTML = qx.html.String.escape(this._formatValue(cellInfo));
      }
    },


    /**
     * Formats a value.
     *
     * @type member
     * @param cellInfo {Map} A map containing the information about the cell to
     *          create. This map has the same structure as in
     *          {@link DataCellRenderer#createDataCell}.
     * @return {String} the formatted value.
     */
    _formatValue : function(cellInfo)
    {
      var value = cellInfo.value;

      if (value == null) {
        return "";
      }
      else if (typeof value == "number")
      {
        if (!qx.ui.table.DefaultDataCellRenderer._numberFormat)
        {
          qx.ui.table.DefaultDataCellRenderer._numberFormat = new qx.util.format.NumberFormat();
          qx.ui.table.DefaultDataCellRenderer._numberFormat.setMaximumFractionDigits(2);
        }

        return qx.ui.table.DefaultDataCellRenderer._numberFormat.format(value);
      }
      else if (value instanceof Date)
      {
        return qx.util.format.DateFormat.getDateInstance().format(value);
      }
      else
      {
        return value;
      }
    },


    /**
     * TODOC
     *
     * @type member
     * @param cellInfo {var} TODOC
     * @param htmlArr {var} TODOC
     * @return {void}
     */
    _createCellStyle_array_join : function(cellInfo, htmlArr)
    {
      qx.ui.table.AbstractDataCellRenderer.prototype._createCellStyle_array_join(cellInfo, htmlArr);

      var stylesToApply = this._getStyleFlags(cellInfo);

      if (stylesToApply & qx.ui.table.DefaultDataCellRenderer.STYLEFLAG_ALIGN_RIGHT) {
        htmlArr.push(";text-align:right");
      }

      if (stylesToApply & qx.ui.table.DefaultDataCellRenderer.STYLEFLAG_BOLD) {
        htmlArr.push(";font-weight:bold");
      }

      if (stylesToApply & qx.ui.table.DefaultDataCellRenderer.STYLEFLAG_ITALIC) {
        htmlArr.push(";font-style:italic");
      }
    },


    /**
     * TODOC
     *
     * @type member
     * @param cellInfo {var} TODOC
     * @param htmlArr {var} TODOC
     * @return {void}
     */
    _createContentHtml_array_join : function(cellInfo, htmlArr) {
      htmlArr.push(qx.html.String.escape(this._formatValue(cellInfo)));
    }
  }
});
